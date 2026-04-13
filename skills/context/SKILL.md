---
name: hams-context
description: boss-hamster/decisions.md 를 현재 세션에 로드 (결정사항 재주입)
allowed-tools:
  - Read
---

# /hams-context

현재 프로젝트의 확정된 결정사항을 세션에 로드합니다.
`/clear` 이후나 새 세션 시작 시 수동으로 실행하세요.

## 동작

1. `{project_root}/.hamstern/boss-hamster/decisions.md` 를 Read 툴로 읽는다
2. 내용을 그대로 컨텍스트에 로드한다
3. 아래 형식으로 확인 출력한다:

```
📌 decisions.md 로드됨 ({n}개 결정사항)
이 세션에서는 위 결정사항들을 따릅니다.
```

## 결정사항 개수 세기

decisions.md 에서 `##` 또는 `- ` 로 시작하는 항목 수를 세어 `{n}` 에 대입한다.
정확하지 않아도 됨 — 대략적인 숫자면 충분.

## project_root 찾기

현재 작업 디렉토리 또는 git root 기준으로
`.hamstern/boss-hamster/decisions.md` 파일을 찾는다.
