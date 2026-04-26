---
name: stop
description: |
  현재 프로젝트에서 햄스턴 후크를 일시 비활성화한다. .hamstern/.disabled 마커 파일을 생성해
  데이터(baby/mom/boss)는 보존하면서 후크 작동만 중단한다. /hams:start 로 재개 가능.
  완전 제거(데이터 삭제)는 rm -rf .hamstern 으로.
  사용법: /hams:stop
allowed-tools:
  - Bash
---

# /hams:stop

현재 프로젝트에서 햄스턴 후크를 **일시 비활성화** 한다. 폴더와 데이터는 보존.

## 동작

1. cwd 에 `.hamstern/` 폴더가 있는지 확인
   - 없음 → "이 프로젝트는 햄스턴이 활성화되지 않았습니다. `/hams:start` 로 활성화하세요." 출력 후 종료
2. `.hamstern/.disabled` 파일을 생성 (빈 파일, 또는 timestamp 한 줄)
   ```bash
   date -u +"%Y-%m-%dT%H:%M:%SZ" > .hamstern/.disabled
   ```
3. 결과 출력:
   ```
   ⏸️  햄스턴 비활성화 (데이터 보존)

   📂 {cwd}/.hamstern/  ← 그대로 유지
   📄 .hamstern/.disabled 생성됨

   이후 Claude Code 세션에서 후크는 silent exit.
   재개:   /hams:start
   완전 제거: rm -rf .hamstern  (⚠️ 모든 데이터 삭제)
   ```

## 왜 폴더 삭제 대신 마커 방식인가

- **데이터 보존**: `baby-hamster/` 의 과거 세션 로그, `boss-hamster/` 의 결정사항이 그대로
- **즉시 재개 가능**: `/hams:start` 한 번이면 마커 제거 + 재활성
- **명확한 의도 분리**:
  · `/hams:stop` = "잠깐 끄기"
  · `rm -rf .hamstern` = "완전 제거 + 데이터 삭제"

## 구현 (체크리스트)

- [ ] `pwd` 확보
- [ ] `[ -d .hamstern ]` 검사 → 없으면 안내 후 종료
- [ ] `touch .hamstern/.disabled` 또는 timestamp 기록
- [ ] 결과 출력
