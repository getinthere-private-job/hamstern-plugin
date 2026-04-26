---
name: start
description: |
  현재 프로젝트에서 햄스턴을 활성화한다. .hamstern/ 폴더와 baby/mom/boss 하위 폴더를 만들고
  메타 파일을 초기화한다. 이후 UserPromptSubmit·Stop 후크가 이 프로젝트에서
  자동으로 동작한다. 이미 활성된 프로젝트에서 다시 실행하면 .disabled 마커를 제거해 재개한다.
  사용법: /hams:start
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# /hams:start

현재 작업 디렉토리에서 **햄스턴을 활성화**한다.

햄스턴 플러그인의 후크는 **`.hamstern/` 폴더가 있는 프로젝트에서만** 동작한다 ([README 참조](../../README.md#-후크-활성화-조건)). 이 스킬은 그 폴더를 한 번에 만들어 준다.

## 동작

다음 작업을 순서대로 수행:

1. 현재 cwd 에 `.hamstern/` 디렉토리 생성 (이미 있으면 그대로 사용)
2. 하위 폴더 생성:
   - `.hamstern/baby-hamster/` — 세션별 사용자 프롬프트 로그 (UserPromptSubmit/Stop 후크가 기록)
   - `.hamstern/mom-hamster/` — 세션 종료 시 요약 (Stop 후크가 기록)
   - `.hamstern/boss-hamster/` — 결정사항 / 핀 (`/hams:dashboard` 가 기록)
3. `.hamstern/config.json` 생성 (이미 있으면 그대로):
   ```json
   {
     "createdAt": "ISO-8601 timestamp",
     "projectName": "<현재 디렉토리 basename>",
     "hooksEnabled": true
   }
   ```
4. `.hamstern/README.md` 생성 — 사용자가 폴더 의미 알도록:
   ```
   # .hamstern/
   햄스턴 데이터 저장소. 이 폴더가 존재하면 햄스턴 후크가 활성화됩니다.
   - baby-hamster/  : 세션 프롬프트 로그
   - mom-hamster/   : 세션 종료 요약
   - boss-hamster/  : 결정사항 (/hams:dashboard)
   비활성화: /hams:stop  (또는 .disabled 파일 생성)
   완전 제거: rm -rf .hamstern  (모든 데이터 삭제)
   ```
5. **`.hamstern/.disabled` 가 있다면 삭제** (`/hams:stop` 으로 일시 비활성화한 상태였다면 재개)
6. 프로젝트 루트의 `.gitignore` 검사:
   - 없으면 안내만 (생성하지 않음)
   - 있으면 `.hamstern/baby-hamster/` 패턴이 있는지 확인. 없으면 사용자에게 추가 의향 묻기 (AskUserQuestion).
     · "baby-hamster 는 세션 로그라 commit 안 하는 게 일반적입니다. .gitignore 에 추가할까요?"
     · 사용자가 OK 하면 `.hamstern/baby-hamster/` 한 줄 append
7. 결과 출력:
   ```
   ✅ 햄스턴 활성화 완료

   📂 {cwd}/.hamstern/
      ├── baby-hamster/   (세션 프롬프트)
      ├── mom-hamster/    (세션 요약)
      ├── boss-hamster/   (결정사항)
      ├── config.json
      └── README.md

   다음 Claude Code 세션부터 후크가 자동 작동합니다.
   대시보드: /hams:dashboard
   비활성화: /hams:stop
   ```

## 구현 (체크리스트)

- [ ] `pwd` 로 현재 cwd 확보
- [ ] `mkdir -p .hamstern/{baby-hamster,mom-hamster,boss-hamster}`
- [ ] `.hamstern/.disabled` 가 있으면 `rm` (일시 비활성 해제)
- [ ] `.hamstern/config.json` 미존재 시 Python 으로 생성 (ISO-8601 timestamp + projectName)
- [ ] `.hamstern/README.md` 미존재 시 Write 로 생성
- [ ] `.gitignore` 존재 + `.hamstern/baby-hamster/` 미포함 → AskUserQuestion → OK 시 append
- [ ] 결과 출력

## 멱등성 (idempotent)

이 스킬은 몇 번 실행해도 안전하다:
- 이미 폴더·파일이 있으면 건드리지 않음
- `.disabled` 만 제거 (재개 의도)
- `.gitignore` 는 중복 추가 방지

## 에러 처리

- 권한 부족 → "현재 디렉토리에 쓰기 권한이 없습니다. 다른 위치에서 실행하세요" 안내
- 디스크 공간 부족 → 시스템 에러 그대로 노출
