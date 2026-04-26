---
name: rule
description: Use when the user wants to register, view, edit, remove, or promote a project rule that should be permanently applied — covers explicit rule capture from current conversation context (add), listing existing rules (list), editing (edit), removal (remove), and manual promotion of provisional why-rules (promote). Trigger phrases - "/hams:rule", "이걸 룰로 만들어줘", "이 패턴 영구 적용", "룰 목록", "룰 수정", "이 원칙 격상".
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# /hams:rule

프로젝트 영구 룰 관리 멀티커맨드 스킬. 사용자가 확신하는 원칙을 `.claude/rules/`에 직접 등록하거나, 기존 룰을 조회/수정/제거/격상한다.

> **`project_root`**: 현재 git 루트 디렉토리 (`git rev-parse --show-toplevel` 결과). git 외부면 `cwd`.
>
> **두 가지 메모리 위치:**
> - `{project_root}/.claude/rules/{topic}.md` — 포인터 (Claude Code 자동 로드, 5~7줄)
> - `{project_root}/.claude/rules/references/{topic}/` — 본문 (rule.md, examples.md, [선택] mockup.html, history.md, lazy)

## 서브커맨드 라우팅

호출 시 첫 인자로 서브커맨드를 받는다. 인자 없이 호출되면 도움말 출력 후 종료.

| 인자 | 동작 |
|------|------|
| `add` | 현재 대화 컨텍스트에서 룰을 추출해 신규 등록 → §`add` 절 |
| `list` | 현재 등록된 모든 룰을 표로 출력 → §`list` 절 |
| `edit {topic}` | 지정 룰의 포인터 + references 파일을 표시 후 사용자 지시대로 수정 → §`edit` 절 |
| `remove {topic}` | 지정 룰 전체 삭제 (포인터 + references 폴더) → §`remove` 절 |
| `promote {topic}` | `.hamstern/why/rules/{topic}.md` 를 영구 룰로 수동 격상 → §`promote` 절 |
| (없음 또는 `help`) | 위 표 출력 후 종료 |

서브커맨드 식별 후 해당 절의 워크플로우만 실행한다. 다른 절은 무시.

## 공통 동작

### baby-hamster 노이즈 차단

`add`, `promote` 는 사용자와 다회 상호작용이 발생하므로 시작 시 마커 ON, 종료 시 OFF:

```bash
mkdir -p .hamstern && touch .hamstern/.deeptalk-running   # 시작
# ...작업...
rm -f .hamstern/.deeptalk-running                          # 종료 (성공/취소/오류 모두)
```

`list`, `edit`, `remove` 는 단일 트랜잭션에 가까워 마커 불필요.

`.hamstern/` 디렉터리가 없는 프로젝트(hamstern 비활성)에서는 마커 생성을 건너뛴다.

### 템플릿 위치

플레이스홀더 채우기 패턴은 `{plugin_root}/skills/rule/templates/` 의 5개 파일 사용. SKILL.md 기준 상대 경로로는 `./templates/` (같은 디렉터리).

### topic 식별자 규칙

- 영어 kebab-case 명사구
- 도메인을 직관적으로 표현
- 예: `ui-alignment`, `table-header-layout`, `data-collection`, `naming-consistency`
- snake_case·camelCase·공백·한글 금지

신규 등록 시 Claude가 자동으로 topic을 제안하되, 사용자가 거부할 수 있어야 함.

---

## §add — 대화 컨텍스트에서 신규 룰 등록

(Task 3에서 채움)

## §list — 등록된 룰 목록 출력

(Task 4에서 채움)

## §edit — 룰 수정

(Task 4에서 채움)

## §remove — 룰 삭제

(Task 4에서 채움)

## §promote — .hamstern/why/rules/ 에서 수동 격상

(Task 5에서 채움)

## Common Mistakes

(전체 작성 완료 후 Task 5에서 채움)
