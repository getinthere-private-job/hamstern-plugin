---
name: remind
description: boss-hamster 의 결정사항(decisions.md)을 현재 세션에 환기. /clear 후 결정사항이 필요한 시점에 명시적으로 호출. CLAUDE.md 안 건드림 — 호출한 그 세션에만 영향.
allowed-tools:
  - Read
  - Bash
---

# /hams:remind

`.hamstern/boss-hamster/decisions.md` 의 결정사항을 현재 세션에 한 번 환기시킨다.

## 왜 자동 주입이 아닌가

- `/clear` = 진짜 컨텍스트 비우기. 거기에 자동으로 뭔가 채워넣으면 GC 효과가 반감된다.
- 모든 작업이 결정사항을 필요로 하지 않는다 — 가벼운 질문엔 빈 컨텍스트가 더 빠르고 정확하다.
- 사용자가 `/hams:remind` 의 출력을 눈으로 보면서 "지금 이 결정들이 적용 중" 인지 의식적으로 인지할 수 있다.

따라서 결정사항 주입은 **사용자가 명시적으로 `/hams:remind` 를 부른 그 시점에만** 일어난다. SessionStart 훅으로 자동 주입하지 않는다.

## 동작

1. (1회) `hooks/migrate_claude_md.py` 로 CLAUDE.md 의 잔존 `<!-- hamstern:decisions:start/end -->` 블록 정리. 마커가 없으면 no-op.
2. `.hamstern/boss-hamster/decisions.md` 존재 확인.
3. 헤더와 본문을 그대로 응답에 포함시켜 출력 — 그 출력 자체가 모델 컨텍스트에 들어간다.

## 실행

```bash
/hams:remind
```

## Claude 실행 절차

1. CLAUDE.md 잔존 마커 정리 (idempotent):
   ```bash
   python3 hooks/migrate_claude_md.py {claude_md_path}
   ```
2. decisions.md 존재 확인 후 본문 출력:
   ```bash
   cat .hamstern/boss-hamster/decisions.md
   ```
3. 출력 후 응답에 한 줄 메모 추가:
   > _위 결정사항이 이 세션에 환기됨. 진짜 컨텍스트 정리는 `/clear`._

decisions.md 가 없을 때:
```
decisions.md 없음.
/hams:dashboard 를 먼저 실행해 결정사항을 확정하세요.
```

## 다른 컨텍스트 정리 방법

진짜 GC (어텐션 비우기) 는 호스트만 가능하다. Claude Code 의 진입점:

| 방법 | GC 강도 |
|---|---|
| `/clear` | 완전 리셋 — 자동 주입 없음. 필요하면 `/hams:remind` 로 따로 환기. |
| `/compact` | 모델이 요약, 일부 보존 — 동일 |
| 새 worktree + 새 세션 | 완전 격리 |

운영 패턴: **`/clear` → (필요시) `/hams:remind`**.
