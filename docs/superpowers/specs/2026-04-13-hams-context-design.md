# hams-context 스킬 디자인

**날짜:** 2026-04-13

## 개요

`/hams-context` 는 현재 프로젝트의 `boss-hamster/decisions.md` 를 읽어 세션 컨텍스트에 로드하는 슬래시 커맨드 스킬입니다. `/clear` 이후처럼 컨텍스트가 초기화된 상황에서 수동으로 결정사항을 재주입할 때 사용합니다.

## 스킬 메타데이터

- **name:** `hams-context`
- **커맨드:** `/hams-context`
- **위치:** `skills/context/SKILL.md`

## 동작

1. `{project_root}/.hamstern/boss-hamster/decisions.md` 읽기
2. 파일 내용을 현재 세션에 로드 (Claude가 직접 읽으므로 컨텍스트에 자동 주입됨)
3. 확인 출력:

```
📌 decisions.md 로드됨 ({n}개 결정사항)
이 세션에서는 위 결정사항들을 따릅니다.
```

## 범위

- 읽는 파일: `boss-hamster/decisions.md` 만
- 요약 없음 — 원본 그대로 로드
- 파일 없을 때 처리 없음

## 관련 스킬

- `hams-audit-decisions` — decisions.md 내용 검토/수정
- `hams-skill-picker` — 스킬 추천 (기존 `hamstern-nagging.md` 참조 → 삭제 예정)
