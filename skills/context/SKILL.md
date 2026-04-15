---
name: context
description: decisions.md를 CLAUDE.md에 주입 — compact 후 결정사항 복구. SessionStart 훅으로 자동 실행됨.
allowed-tools:
  - Read
  - Bash
---

# /hams-context

프로젝트의 확정된 결정사항을 CLAUDE.md에 주입합니다.

## 동작

1. `.hamstern/boss-hamster/decisions.md` 존재 확인
2. `hooks/inject_decisions.py`로 CLAUDE.md 마커 섹션 업데이트
3. 완료 출력

## 실행

```bash
/hams-context
```

## 출력 예시

decisions.md 있을 때:
```
📌 decisions.md 로드됨 (12개 결정사항)
CLAUDE.md 마커 섹션 업데이트 완료.
이 세션에서는 위 결정사항들을 따릅니다.
```

decisions.md 없을 때:
```
decisions.md 없음.
/hams-dashboard를 먼저 실행해 결정사항을 확정하세요.
```

## 자동화

`.claude/settings.json`의 `SessionStart` 훅이 설정되면 compact/재시작 시 자동 실행.

## Claude 실행 절차

decisions.md 경로 확인 후:
```bash
python3 hooks/inject_decisions.py {decisions_path} {claude_md_path}
```
결과 확인 후 `- ` 항목 수를 세어 출력.
