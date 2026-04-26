# /hams:why 격상 메커니즘 + /hams:rule 신규 스킬 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/hams:why` 가 발견한 잠정 룰을 재발 시 영구 자산(`.claude/rules/`)으로 격상하는 메커니즘과, 사용자가 직접 룰을 등록·관리하는 `/hams:rule` 멀티커맨드 스킬을 추가한다.

**Architecture:** 2-tier 메모리 구조 — `.claude/rules/{topic}.md`(포인터, 항상 자동 로드) + `.claude/rules/references/{topic}/`(본문, lazy). 진단 경로(`/hams:why`)는 `.hamstern/why/rules/` 격리 후 재발 시 격상. 직접 등록 경로(`/hams:rule add`)는 격리 단계 우회. 두 경로 모두 동일한 파일 구조 산출.

**Tech Stack:** 순수 markdown SKILL.md 파일. 도구: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion. 외부 의존성 없음.

**Background:** 설계 합의 문서는 [`docs/discussions/2026-04-26-why-rule-promotion-design.md`](../discussions/2026-04-26-why-rule-promotion-design.md) 참고. 이 플랜은 그 결정을 코드(스킬 markdown)로 옮기는 작업.

---

## File Structure

### 새로 생성

```
skills/rule/
├── SKILL.md                              # 멀티커맨드 라우터 + 5개 서브커맨드 본문
└── templates/
    ├── pointer.md                        # .claude/rules/{topic}.md 템플릿
    ├── rule.md                           # references/{topic}/rule.md 템플릿
    ├── examples.md                       # references/{topic}/examples.md 템플릿
    ├── mockup.html                       # references/{topic}/mockup.html 템플릿 (디자인 타입)
    └── history.md                        # references/{topic}/history.md 템플릿
```

### 수정

```
skills/why/SKILL.md                       # 격상 메커니즘 추가 (신규 Step 1.5, Step 5 갱신, 완료 메시지 수정)
.claude-plugin/marketplace.json           # skills 배열에 "./skills/rule" 추가
README.md                                 # "Rules System" 섹션 신설
```

### 산출물 (런타임에 사용자 프로젝트에 생성됨 — 이 플랜은 안 만짐)

```
{user-project}/.claude/rules/{topic}.md           # 포인터 (Claude Code 자동 로드)
{user-project}/.claude/rules/references/{topic}/  # 본문 (lazy)
{user-project}/.hamstern/why/rules/{topic}.md     # /hams:why 잠정 보관 — 격상 후 "격상됨" 마커
```

---

## Acceptance Criteria (구현 완료 후 동작해야 하는 시나리오)

### S1. /hams:why 1회차 (잠정 저장)
사용자가 `/hams:why` 호출 → 근본 원인 도출 → `.hamstern/why/rules/{topic}.md` 저장 → 완료 메시지에 **"추후 동일 문제 재발 시 영구 rule 격상이 제안됩니다"** 포함.

### S2. /hams:why 2회차 (매칭 → 격상 제안)
이전과 동일한 원칙이 발동 → 1단계에서 `.hamstern/why/rules/`에서 매칭 → 사용자에게 **"`.claude/rules/`로 격상하시겠습니까?"** 질문 → 승인 → 적용 범위(전역/특정 경로) 질문 → 포인터 + references 생성 → 원본에 `> 격상됨 → ... (날짜)` 마커 추가.

### S3. /hams:rule add (직접 등록)
사용자가 대화 중 어떤 패턴을 도출 후 `/hams:rule add` 호출 → 컨텍스트에서 자동 추출 (원칙·트리거·코드/디자인·타입) → 1차 초안 + 자동 판정한 타입 표시 → 사용자가 검수/수정 → 적용 범위 질문 → `.claude/rules/{topic}.md` 및 references/ 생성. **`.hamstern/`에 어떤 파일도 만들지 않음.**

### S4. /hams:rule list
현재 `.claude/rules/*.md` (references 폴더 제외) 목록을 표 형식으로 출력 — topic, 원칙 한 문장, 트리거, 적용 범위.

### S5. /hams:rule edit {topic}
지정 topic의 포인터 + references 파일을 모두 읽어 사용자에게 표시 → "어디를 어떻게 수정할까요?" → 사용자 지시대로 Edit.

### S6. /hams:rule remove {topic}
지정 topic 존재 확인 → 삭제 대상 파일 목록 표시 → 확인 → 포인터와 references/{topic}/ 디렉터리 전체 삭제.

### S7. /hams:rule promote {topic}
사용자가 `.hamstern/why/rules/{topic}.md` 를 명시적으로 격상 → S2와 동일한 격상 워크플로우.

### S8. 디자인 타입 자동 판정
`/hams:rule add` 가 컨텍스트에 HTML/CSS/JSX/className/styling 키워드 우세 시 → 타입 = "디자인" → 1차 초안에 표시 → mockup.html 추가 생성.

### S9. baby-hamster 노이즈 차단
`/hams:rule add`, `/hams:why`, `/hams:rule promote` 가 대화 중에 `.hamstern/.deeptalk-running` 마커 ON → 종료(성공/취소/오류) 시 OFF.

### S10. marketplace.json 인식
플러그인 재로드 시 `/hams:rule` 명령어가 `/help` 에 표시되고 호출 가능.

---

### Task 1: rule 스킬 디렉터리 + 템플릿 5종 생성

**Files:**
- Create: `skills/rule/templates/pointer.md`
- Create: `skills/rule/templates/rule.md`
- Create: `skills/rule/templates/examples.md`
- Create: `skills/rule/templates/mockup.html`
- Create: `skills/rule/templates/history.md`

이 템플릿들은 `/hams:rule add`, `/hams:rule promote`, `/hams:why` 격상 시 모두 동일하게 사용된다. 단일 출처로 관리하기 위해 별도 파일로 분리.

#### Step 1.1: 디렉터리 생성

```bash
mkdir -p skills/rule/templates
```

#### Step 1.2: 포인터 템플릿 작성

Create `skills/rule/templates/pointer.md`:

```markdown
{{paths_frontmatter}}## {{title}}

**원칙:** {{principle}}
**적용 트리거:** {{trigger}}
**자세히 (트리거 매칭 시 순서대로 읽기):**
  1. references/{{topic}}/rule.md
{{mockup_line}}  {{n}}. references/{{topic}}/examples.md
```

플레이스홀더:
- `{{paths_frontmatter}}` → 전역이면 빈 문자열, 특정 경로면 다음 블록 (포인터 파일 맨 앞에 들어감, 한 줄 띄움 포함):
  ```
  ---
  paths:
    - "src/components/**"
  ---
  
  ```
- `{{title}}` → 한국어 원칙명 (예: "테이블 헤더 레이아웃")
- `{{principle}}` → 한 문장 원칙
- `{{trigger}}` → "Table/DataGrid/List 컴포넌트 작성 시" 같은 발동 조건
- `{{topic}}` → kebab-case 식별자 (예: `table-header-layout`)
- `{{mockup_line}}` → 디자인 타입이면 `  2. references/{{topic}}/mockup.html`, 아니면 빈 문자열
- `{{n}}` → mockup이 있으면 3, 없으면 2

#### Step 1.3: rule.md 템플릿

Create `skills/rule/templates/rule.md`:

```markdown
# {{title}} — 원칙 본문

**발견:** {{date}}
**트리거 맥락:** {{trigger_context}}

## 표면 원인
{{surface_cause}}

## 근본 원인
{{root_cause}}

## 원칙
{{principle}}

## 근거
{{rationale}}
```

플레이스홀더:
- `{{date}}` → YYYY-MM-DD
- `{{trigger_context}}` → 어떤 코드/문제에서 발견됐는지
- `{{surface_cause}}` → 증상 수준 원인
- `{{root_cause}}` → 원칙 수준 원인
- `{{rationale}}` → 왜 이 원칙이어야 하는지 (선택, 비어 있어도 됨)

#### Step 1.4: examples.md 템플릿

Create `skills/rule/templates/examples.md`:

````markdown
# {{title}} — 코드 패턴

## ✅ 올바른 패턴

```{{lang}}
{{good_example}}
```

{{flow_section}}

## ❌ 잘못된 패턴

```{{lang}}
{{bad_example}}
```

{{found_in_section}}
````

플레이스홀더:
- `{{lang}}` → `tsx`, `ts`, `py` 등
- `{{good_example}}` → 올바른 코드
- `{{bad_example}}` → 잘못된 코드 (선택, 없으면 "## ❌ 잘못된 패턴" 섹션 통째로 생략)
- `{{flow_section}}` → 코드 타입에서 흐름 다이어그램이 있을 때만:
  ```
  ## 흐름 (텍스트 다이어그램)
  
      요청 → 검증 → 처리 → 응답
  ```
  없으면 빈 문자열
- `{{found_in_section}}` → 발견된 실제 사례 목록 (한 줄당 한 사례):
  ```
  ## 발견된 실제 사례
  - {{file_path}} ({{date}}) — {{note}}
  ```

#### Step 1.5: mockup.html 템플릿 (디자인 타입 전용)

Create `skills/rule/templates/mockup.html`:

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Rule: {{title}}</title>
<style>
body { font-family: -apple-system, sans-serif; padding: 20px; max-width: 900px; margin: 0 auto; }
h1 { border-bottom: 2px solid #333; padding-bottom: 8px; }
h2 { margin-top: 32px; }
.example { border: 1px solid #ddd; border-radius: 6px; padding: 16px; margin: 12px 0; }
.bad { border-color: #c33; background: #fdd; }
.good { border-color: #393; background: #dfd; }
.label { font-weight: bold; margin-bottom: 8px; }
{{custom_css}}
</style>
</head>
<body>
<h1>{{title}}</h1>
<p><strong>원칙:</strong> {{principle}}</p>

<h2>✅ 올바른 패턴</h2>
<div class="example good">
<div class="label">good example</div>
{{good_html}}
</div>

<h2>❌ 잘못된 패턴</h2>
<div class="example bad">
<div class="label">bad example</div>
{{bad_html}}
</div>
</body>
</html>
```

플레이스홀더:
- `{{custom_css}}` → 룰별 추가 CSS (예: `.table-header { display: flex; justify-content: space-between; }`)
- `{{good_html}}` → 올바른 HTML 마크업
- `{{bad_html}}` → 잘못된 HTML 마크업 (선택)

#### Step 1.6: history.md 템플릿

Create `skills/rule/templates/history.md`:

```markdown
# {{title}} — 발견·재발 이력

## 등록 정보
- **등록일:** {{date}}
- **등록 경로:** {{registration_path}}

## 발견 이력
{{discovery_log}}

## 재발 이력 (격상 후 누적)
{{recurrence_log}}
```

플레이스홀더:
- `{{registration_path}}` → 둘 중 하나:
  - `"/hams:why 격상 (.hamstern/why/rules/{topic}.md → .claude/rules/)"`
  - `"/hams:rule add (수동 등록)"`
  - `"/hams:rule promote (수동 격상)"`
- `{{discovery_log}}` → 한 줄당 한 발견:
  ```
  - **{date}** — {file_or_context}: {note}
  ```
- `{{recurrence_log}}` → 등록 직후엔 비어 있거나 `(아직 없음)`. 이후 같은 룰 재발 시 append.

#### Step 1.7: 커밋

```bash
git add skills/rule/templates/
git commit -m "feat(rule): add rule file templates (pointer, rule, examples, mockup, history)"
```

#### 검증
- `ls skills/rule/templates/` → 5개 파일 존재
- 각 파일에 플레이스홀더 `{{...}}` 가 정확히 정의된 대로 들어 있는지 grep:
  ```bash
  grep -l "{{title}}" skills/rule/templates/*.md
  ```
  Expected: pointer.md, rule.md, examples.md, history.md (4개)

---

### Task 2: /hams:rule 스킬 스캐폴딩 (frontmatter + 라우터 + Overview)

**Files:**
- Create: `skills/rule/SKILL.md`

이 단계에서는 라우터와 공통 섹션만 만든다. 각 서브커맨드 본문은 Task 3~7에서 채운다.

#### Step 2.1: SKILL.md 골격 작성

Create `skills/rule/SKILL.md`:

```markdown
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

플레이스홀더 채우기 패턴은 `{plugin_root}/skills/rule/templates/` 의 5개 파일 사용. plugin_root는 이 스킬 파일의 상위 두 단계 (즉 SKILL.md 기준 `../templates/`).

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

(전체 작성 완료 후 Task 6에서 채움)
```

#### Step 2.2: 검증 — frontmatter 형식 점검

Run:
```bash
head -20 skills/rule/SKILL.md
```

Expected: `name: rule`, `description: Use when...`, `allowed-tools` 7개 항목 (Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion).

#### Step 2.3: 커밋

```bash
git add skills/rule/SKILL.md
git commit -m "feat(rule): scaffold /hams:rule multi-command skill (router + common sections)"
```

---

### Task 3: §add 서브커맨드 본문 작성

**Files:**
- Modify: `skills/rule/SKILL.md` (§add 절 채움)

가장 복잡한 서브커맨드. skill-creator 패턴(컨텍스트 추출 + 미리보기 + 승인)을 차용하되, 룰 도메인에 맞게 변형.

#### Step 3.1: §add 절 본문 작성

Edit `skills/rule/SKILL.md`, replace `## §add — 대화 컨텍스트에서 신규 룰 등록\n\n(Task 3에서 채움)` with:

````markdown
## §add — 대화 컨텍스트에서 신규 룰 등록

호출 즉시 다음 단계를 순서대로 수행한다.

### Step A0: deep-talk 마커 ON

```bash
mkdir -p .hamstern && touch .hamstern/.deeptalk-running
```

`.hamstern/` 미존재 프로젝트면 건너뜀. 모든 종료 경로에서 `rm -f` 필수.

### Step A1: 컨텍스트 추출

현재 세션의 다음 정보를 분석한다.

- 사용자 발화 (최근 N턴 — 최소 패턴이 도출되기 시작한 지점부터)
- 대화 중 등장한 코드 스니펫 (Bash/Edit/Write/Read 결과 또는 사용자가 붙여넣은 코드)
- 사용자가 강조한 제약·원칙 (예: "왼쪽엔 검색, 오른쪽엔 정렬", "캐시 먼저 확인", "이름은 동사+명사")
- 작업 도메인 (어떤 파일/컴포넌트/모듈에서 패턴이 도출됐나)

다음을 도출:
- **원칙 후보** — 한 문장
- **적용 트리거 후보** — 어떤 작업/키워드에서 발동
- **타입 후보** — 코드 / 디자인 / 둘 다 (Step A2 판정 휴리스틱)
- **결과물 후보** — 코드 스니펫(올바른/잘못된)과/또는 HTML 마크업

### Step A2: 타입 자동 판정 (휴리스틱)

다음 키워드/신호 비율로 결정:

| 신호 | 타입 |
|------|------|
| HTML 태그, CSS 속성, className, Tailwind, layout, flex, grid, padding, margin, color, font, 정렬, 여백, mockup, UI, 컴포넌트 시각 배치 | 디자인 |
| function, async, await, return, API, fetch, query, algorithm, 데이터 흐름, validation, 상태 관리, 캐시, 검증 로직 | 코드 |
| 양쪽 신호 모두 강함 (예: 디자인 시스템 + 함수 시그니처) | 둘 다 |

기본값: 모호하면 **코드**.

판정 결과는 1차 초안에 명시적으로 표시 → 사용자가 거부 가능.

### Step A3: 1차 초안 미리보기

다음 형식으로 초안을 화면에 출력한다 (파일은 아직 안 만듦):

```
다음 룰을 만들려고 합니다:

  topic       : table-header-layout
  원칙        : 테이블 헤더는 좌상=검색/필터, 우상=정렬/액션으로 분리한다
  적용 트리거 : Table/DataGrid/List 컴포넌트 작성 시
  타입        : 디자인 (mockup.html 포함)
  결과물      : 
    ✅ 좋은 예시 — ProjectsTable.tsx 의 헤더 패턴 (코드 + HTML mockup)
    ❌ 나쁜 예시 — 정렬이 좌측·검색이 중앙인 배치

이 내용으로 진행할까요?
```

### Step A4: 검수 루프 (`AskUserQuestion`)

옵션 4개:

1. **이대로 진행** → Step A5
2. **수정할 게 있어요** → 사용자가 자유 텍스트로 수정 지시 → Step A1~A3 다시 (영향받는 부분만 갱신, 그대로인 건 유지) → 다시 Step A4
3. **타입 변경** → "코드 / 디자인 / 둘 다" 중 선택 → A3 재출력 → A4 재진행
4. **취소** → 마커 OFF 후 종료. 아무것도 저장하지 않음.

검수 루프는 최대 5회까지 (사용자가 5회 이후에도 미확정이면 "현재 초안으로 저장 / 취소" 양자택일로 좁힘).

### Step A5: 적용 범위 질문 (`AskUserQuestion`)

```
적용 범위를 선택하세요:
1. 전역 (모든 작업에서 항상 로드)
2. 특정 경로 한정 (예: src/components/**, src/api/**)
```

옵션 2 선택 시 후속 질문: "어떤 경로 글로브를 사용할까요? (쉼표로 여러 개 가능)" → 사용자 입력을 그대로 paths frontmatter에 넣음.

### Step A6: topic 식별자 결정

Step A3 초안의 topic을 그대로 쓰되, 다음 충돌 검사:

```bash
ls .claude/rules/{topic}.md 2>/dev/null
```

존재하면 `AskUserQuestion`:
1. 덮어쓰기
2. 새 이름 (사용자 입력)
3. 취소 → 마커 OFF, 종료

### Step A7: 파일 생성

순서:

```bash
mkdir -p .claude/rules/references/{topic}
```

각 파일 생성 (Write 사용):

1. **포인터** `.claude/rules/{topic}.md` — `{plugin_root}/skills/rule/templates/pointer.md` 읽고 플레이스홀더 치환 후 Write.
   - 적용 범위 = 전역이면 `{{paths_frontmatter}}` → `""`
   - 특정 경로면 `{{paths_frontmatter}}` → 다음 (마지막 빈 줄 포함):
     ```
     ---
     paths:
       - "src/components/**"
     ---
     
     ```
   - 디자인/둘 다 타입이면 `{{mockup_line}}` → `  2. references/{topic}/mockup.html\n`, `{{n}}` → `3`
   - 코드 타입이면 `{{mockup_line}}` → `""`, `{{n}}` → `2`

2. **rule.md** `.claude/rules/references/{topic}/rule.md` — `templates/rule.md` 치환 후 Write.
   - `{{date}}` → `date +%F` 또는 시스템 오늘 날짜
   - `{{trigger_context}}` → Step A1에서 도출한 작업 도메인 한 줄 ("ProjectsTable.tsx 헤더 작업 중")
   - `{{surface_cause}}` → 표면 증상 (사용자 강조 표현 그대로)
   - `{{root_cause}}` → 원칙 수준 원인 (Claude가 추론한 근본)
   - `{{principle}}` → 한 문장 원칙
   - `{{rationale}}` → 사용자가 언급한 근거 (없으면 비움)

3. **examples.md** `.claude/rules/references/{topic}/examples.md` — `templates/examples.md` 치환.
   - `{{lang}}` → 코드 추출에서 추론 (`tsx`, `py`, `ts`, …)
   - `{{good_example}}` → 컨텍스트에서 도출한 올바른 패턴
   - `{{bad_example}}` 비어 있으면 `## ❌ 잘못된 패턴\n\n```{{lang}}\n{{bad_example}}\n```` 섹션 전체 삭제 후 Write
   - `{{flow_section}}` 비어 있으면 빈 문자열
   - `{{found_in_section}}` → `발견된 실제 사례\n- {파일경로} ({날짜}) — 등록 시점` 한 줄

4. **mockup.html** (디자인/둘 다 타입만) `.claude/rules/references/{topic}/mockup.html` — `templates/mockup.html` 치환.
   - `{{good_html}}` → 컨텍스트의 좋은 HTML 마크업
   - `{{bad_html}}` 비어 있으면 `<h2>❌ 잘못된 패턴</h2>` 블록 통째로 삭제 후 Write
   - `{{custom_css}}` → 룰별 CSS (필요 시)

5. **history.md** `.claude/rules/references/{topic}/history.md` — `templates/history.md` 치환.
   - `{{registration_path}}` → `"/hams:rule add (수동 등록)"`
   - `{{discovery_log}}` → `- **{date}** — {file_or_context}: 등록 시점 1차 패턴 도출`
   - `{{recurrence_log}}` → `(아직 없음)`

### Step A8: 마커 OFF + 완료 메시지

```bash
rm -f .hamstern/.deeptalk-running
```

출력:

```
✅ 룰 등록 완료
   포인터    : .claude/rules/{topic}.md
   본문      : .claude/rules/references/{topic}/
   적용 범위 : {전역 / paths: ...}
   타입      : {코드 / 디자인 / 둘 다}

▶ 다음 세션부터 자동으로 컨텍스트에 로드됩니다.
```

### Step A9: 자가검증

작성 직후 다음을 확인:
- `.claude/rules/{topic}.md` 가 5~10줄 사이인가? (포인터는 짧아야 함)
- 디자인/둘 다 타입이면 `mockup.html` 이 실제로 존재하는가?
- `references/{topic}/` 안에 `rule.md`, `examples.md`, `history.md` 가 있는가?
- 포인터 frontmatter 가 paths 옵션 선택과 일치하는가?

검증 실패 시 사용자에게 어떤 검증이 실패했는지 보고 + 작성한 파일 경로를 알려주고 종료 (수동 정정 가능).

````

#### Step 3.2: 커밋

```bash
git add skills/rule/SKILL.md
git commit -m "feat(rule): implement /hams:rule add (context extraction + type detection + draft loop)"
```

---

### Task 4: §list, §edit, §remove 서브커맨드 본문

**Files:**
- Modify: `skills/rule/SKILL.md`

세 서브커맨드는 단순해서 한 작업으로 묶음.

#### Step 4.1: §list 절 작성

Edit, replace `## §list — 등록된 룰 목록 출력\n\n(Task 4에서 채움)` with:

````markdown
## §list — 등록된 룰 목록 출력

### Step L1: 룰 파일 수집

```bash
ls .claude/rules/*.md 2>/dev/null
```

대상은 `.claude/rules/` 직속 `.md` 파일만 (references/ 하위는 제외).

파일이 없으면 다음 메시지 출력 후 종료:

```
📂 등록된 룰이 없습니다.
   새 룰 등록    : /hams:rule add
   why로 시작    : /hams:why "...문제 설명..."
```

### Step L2: 각 포인터 파싱

각 파일에 대해:
- 파일명 → topic (확장자 제거)
- 본문에서 `## ` 헤더 라인 → 원칙명
- `**원칙:**` 라인 → 원칙 한 문장
- `**적용 트리거:**` 라인 → 트리거
- frontmatter `paths:` 존재 여부 → 적용 범위 (전역 / paths 목록)

### Step L3: 표 출력

다음 형식으로 출력:

```
📋 등록된 룰 ({n}건)

| topic | 원칙 | 트리거 | 적용 범위 |
|-------|------|--------|-----------|
| table-header-layout | 헤더는 좌상=검색, 우상=정렬 | Table 작성 시 | 전역 |
| api-cache-first | API 호출 전 캐시 확인 | fetch/query 작업 시 | src/api/** |

상세 보기 : /hams:rule edit {topic}
삭제      : /hams:rule remove {topic}
```

원칙·트리거가 너무 길면 60자에서 truncate + `…`.
````

#### Step 4.2: §edit 절 작성

Edit, replace `## §edit — 룰 수정\n\n(Task 4에서 채움)` with:

````markdown
## §edit — 룰 수정

### Step E1: topic 인자 검증

호출: `/hams:rule edit {topic}`

`{topic}` 인자 없으면:
```
사용법: /hams:rule edit {topic}
현재 룰 목록은 /hams:rule list
```
출력 후 종료.

### Step E2: 파일 존재 확인

```bash
test -f .claude/rules/{topic}.md && test -d .claude/rules/references/{topic}
```

둘 중 하나라도 없으면:
```
❌ {topic} 룰을 찾을 수 없습니다.
   등록된 룰    : /hams:rule list
   잠정 룰 격상 : /hams:rule promote {topic}
```

### Step E3: 모든 관련 파일 표시

다음을 모두 Read 하여 사용자에게 노출:

- `.claude/rules/{topic}.md` (포인터)
- `.claude/rules/references/{topic}/rule.md`
- `.claude/rules/references/{topic}/examples.md`
- `.claude/rules/references/{topic}/mockup.html` (있을 때만)
- `.claude/rules/references/{topic}/history.md`

각 파일을 코드 블록으로 출력. 그 다음 묻는다:

```
어디를 어떻게 수정할까요?
예) "원칙 문장을 'X'로 바꿔줘", "examples에 좋은 예시 코드 추가해줘", "paths를 src/api/**로 좁혀줘"
```

### Step E4: 사용자 지시 적용

사용자 응답을 받아 정확한 Edit 도구 호출로 변환. 한 번에 여러 파일 수정 가능. 모호하면 "다음을 수정합니다: ... 진행할까요?" AskUserQuestion 으로 1회 확인.

### Step E5: 완료 메시지

```
✅ 룰 수정 완료
   수정된 파일:
     - .claude/rules/{topic}.md
     - .claude/rules/references/{topic}/rule.md (예시)
```
````

#### Step 4.3: §remove 절 작성

Edit, replace `## §remove — 룰 삭제\n\n(Task 4에서 채움)` with:

````markdown
## §remove — 룰 삭제

### Step R1: topic 인자 검증

호출: `/hams:rule remove {topic}`

`{topic}` 없으면 §edit 와 동일하게 사용법 출력 후 종료.

### Step R2: 존재 확인 + 삭제 대상 표시

```bash
test -f .claude/rules/{topic}.md
```

없으면:
```
❌ {topic} 룰이 없습니다.
   현재 룰 목록 : /hams:rule list
```

존재하면 다음 출력:

```
다음을 삭제합니다:
  - .claude/rules/{topic}.md (포인터)
  - .claude/rules/references/{topic}/ (폴더 전체)
    └ rule.md, examples.md, [mockup.html], history.md
```

### Step R3: 확인 (`AskUserQuestion`)

옵션 2개:
1. 삭제 진행
2. 취소

### Step R4: 삭제

승인 시:

```bash
rm .claude/rules/{topic}.md
rm -rf .claude/rules/references/{topic}/
```

### Step R5: 완료 메시지

```
🗑️  {topic} 룰 삭제 완료
   포인터 + references 폴더 모두 제거됨
```

(연관된 `.hamstern/why/rules/{topic}.md` 가 있어도 건드리지 않음 — 그건 별개 자산.)
````

#### Step 4.4: 커밋

```bash
git add skills/rule/SKILL.md
git commit -m "feat(rule): implement /hams:rule list/edit/remove subcommands"
```

---

### Task 5: §promote 서브커맨드 본문

**Files:**
- Modify: `skills/rule/SKILL.md`

`/hams:why` 가 자동으로 격상하는 로직과 동일한 변환을 사용자 명시 호출로 실행.

#### Step 5.1: §promote 절 작성

Edit, replace `## §promote — .hamstern/why/rules/ 에서 수동 격상\n\n(Task 5에서 채움)` with:

````markdown
## §promote — .hamstern/why/rules/ 에서 수동 격상

`/hams:why` 가 매칭하지 못했지만 사용자가 "이건 격상해야겠다" 싶을 때 명시적으로 트리거.

### Step P1: 마커 ON

```bash
mkdir -p .hamstern && touch .hamstern/.deeptalk-running
```

### Step P2: topic 인자 검증

호출: `/hams:rule promote {topic}`

`{topic}` 없으면:
```
사용법: /hams:rule promote {topic}
잠정 룰 목록 확인:
  ls .hamstern/why/rules/
```
출력 후 마커 OFF, 종료.

### Step P3: 원본 존재 확인

```bash
test -f .hamstern/why/rules/{topic}.md
```

없으면:
```
❌ .hamstern/why/rules/{topic}.md 가 없습니다.
   확인: ls .hamstern/why/rules/
```
마커 OFF, 종료.

### Step P4: 이미 격상됐는지 확인

원본 파일 첫 5줄에 `> 격상됨` 패턴이 있으면:
```
ℹ️  {topic} 은 이미 격상되었습니다.
   현재 위치: .claude/rules/{topic}.md
```
마커 OFF, 종료.

### Step P5: 원본 읽기 + 자동 분류

`.hamstern/why/rules/{topic}.md` 의 내용을 읽고 다음을 추출:

- `**표면 원인:**`
- `**근본 원인:**`
- `**원칙:**`
- `**트리거:**` (등록 당시 발견 계기)
- `**발견:**` 날짜

타입 판정: 원본에 코드 스니펫이 있는지 확인.
- HTML/CSS/JSX 마크업이 있으면 → 디자인
- 코드만 있으면 → 코드
- 둘 다 → 둘 다
- 아무 코드도 없으면 → 코드 (기본)

### Step P6: 적용 범위 질문 (`AskUserQuestion`)

§add Step A5와 동일.

### Step P7: 파일 생성

§add Step A7 과 동일하지만 입력 소스가 다름:
- 원칙·표면·근본 원인은 `.hamstern/why/rules/{topic}.md` 에서 가져옴
- 코드 예시는 원본에 있는 것을 사용 (없으면 `examples.md` 의 `{{good_example}}` 비워두고 사용자에게 "좋은 예시를 추가하고 싶으면 /hams:rule edit {topic} 를 사용하세요" 안내)
- `history.md` 의 `{{registration_path}}` → `"/hams:rule promote (수동 격상)"`
- `history.md` 의 `{{discovery_log}}` → 원본의 발견·재발 정보 그대로 옮김

### Step P8: 원본에 격상 마커 추가

`.hamstern/why/rules/{topic}.md` 의 맨 위(frontmatter 다음, 본문 시작 전)에 다음 라인을 Edit으로 삽입:

```
> 격상됨 → .claude/rules/{topic}.md ({YYYY-MM-DD})
```

### Step P9: 마커 OFF + 완료 메시지

```bash
rm -f .hamstern/.deeptalk-running
```

```
🚀 {topic} 영구 룰로 격상
   포인터    : .claude/rules/{topic}.md
   본문      : .claude/rules/references/{topic}/
   원본 마커 : .hamstern/why/rules/{topic}.md (격상됨 표시)
```

### Step P10: 자가검증

§add Step A9 와 동일.
````

#### Step 5.2: Common Mistakes 섹션 작성

Edit, replace `## Common Mistakes\n\n(전체 작성 완료 후 Task 6에서 채움)` with:

```markdown
## Common Mistakes

- **`/hams:rule add` 호출 시 컨텍스트가 비어 있는데도 진행** → 1차 초안이 의미 없는 placeholder가 됨. 컨텍스트가 부족하면 "최근 대화에서 패턴을 추출할 수 없습니다. 어떤 원칙인지 직접 알려주세요."로 폴백.
- **topic을 한국어/snake_case로 생성** → kebab-case 영문 명사구 강제. `테이블헤더` ❌ → `table-header-layout` ✅.
- **포인터에 본문을 다 욱여넣음** → 토큰 부채. 포인터는 5~10줄, 자세한 건 references/.
- **mockup.html을 코드 타입 룰에도 생성** → 불필요. Step A2 타입 판정 결과를 따른다.
- **paths frontmatter 인용 부호 누락** → `paths:` 의 글로브는 따옴표 필수 (`"src/components/**"`). 따옴표 빼면 YAML 파서 에러.
- **`.hamstern/.deeptalk-running` 마커 정리 누락** → baby-hamster 노이즈. add/promote 의 모든 종료 경로(성공/취소/오류)에서 `rm -f`.
- **promote 시 원본 그대로 두고 마커도 안 박음** → 다음 호출 시 "이미 격상됐는지" 판단 불가. Step P8 필수.
- **edit/remove 가 references 폴더 빠뜨림** → edit는 references 까지 모두 표시·수정 대상, remove는 폴더 전체 `rm -rf`.
- **list 가 references/*.md 도 룰로 표시** → `.claude/rules/*.md` glob은 `.claude/rules/references/...` 를 포함하지 않음을 확인. shell glob은 직속만, 재귀는 `**` 필요.
```

#### Step 5.3: 커밋

```bash
git add skills/rule/SKILL.md
git commit -m "feat(rule): implement /hams:rule promote + Common Mistakes section"
```

---

### Task 6: /hams:why 격상 메커니즘 추가

**Files:**
- Modify: `skills/why/SKILL.md`

기존 4단계 추론 후 5단계 저장 → 6단계 완료 메시지 흐름에서, 1단계의 매칭 동작을 확장하고 신규 1.5단계(격상 제안)를 추가. 5단계 메시지에 격상 안내 추가.

#### Step 6.1: 기존 SKILL.md 백업 및 읽기 (Edit 사용 전 확인)

```bash
cat skills/why/SKILL.md
```

(이미 위 컨텍스트에 있는 내용 — 1단계: 기존 rules 확인, 2: 가설, 3: 서브에이전트, 4: 추론, 5: 저장, 6: 완료 메시지)

#### Step 6.2: Step 1 확장 — 매칭 시 격상 분기 추가

Edit `skills/why/SKILL.md`, replace:

```
### 1. 기존 rules 확인

`{project_root}/.hamstern/why/rules/` 폴더가 있으면 기존 원칙들을 읽어 문제와 매칭 시도.
원칙이 현재 문제의 증상과 직접 일치하면 해당 원칙을 인용하고 조사를 종료합니다. 그렇지 않으면 2단계로 진행합니다.
```

with:

```
### 1. 기존 rules 확인

다음 두 위치의 룰을 확인한다 (순서대로):

1. `{project_root}/.claude/rules/` — 영구 격상된 룰. 매칭되면 해당 포인터를 인용 + references/ 의 rule.md 를 읽어 적용 가이드 제공 후 조사 종료.
2. `{project_root}/.hamstern/why/rules/` — 잠정 룰. 매칭되면 **Step 1.5 격상 제안**으로 진행.

매칭 판정: 원칙(`**원칙:**` 라인)이 현재 문제 증상과 직접 일치하는가. 단순 키워드 겹침이 아니라 인과적으로 같은 문제인지 판단.

매칭되지 않으면 2단계로 진행.

### 1.5. 격상 제안 (Step 1에서 .hamstern/why/rules 매칭 시만)

매칭된 잠정 룰이 다시 발동했음을 의미 → 영구 격상 적기.

다음 메시지 출력:

```
🔁 동일 원칙이 재발했습니다.
   잠정 룰   : .hamstern/why/rules/{topic}.md
   원칙      : {원칙 한 문장}
   첫 발견   : {원본의 발견 날짜}

이 룰을 .claude/rules/ 로 영구 격상하시겠습니까?
```

`AskUserQuestion` 옵션 3개:
1. 네, 격상합니다 → Step 1.5.1로
2. 아니오, 이번에도 잠정 유지 → 원본의 history 섹션에 재발 한 줄 append 후 조사 종료
3. 새로 조사하고 싶어요 (원칙이 다를 수도) → Step 2로 진행 (정상 흐름)

#### Step 1.5.1: 적용 범위 질문

(`/hams:rule add` Step A5 와 동일 — `AskUserQuestion`으로 전역/특정 경로 선택)

#### Step 1.5.2: 격상 실행

`/hams:rule promote {topic}` Step P5~P10 과 동일한 변환을 인라인으로 수행:
- 원본 읽기 → 타입 자동 판정
- `.claude/rules/{topic}.md` (포인터) Write
- `.claude/rules/references/{topic}/` 디렉토리 + rule.md/examples.md/[mockup.html]/history.md Write
- 원본 `.hamstern/why/rules/{topic}.md` 맨 위에 `> 격상됨 → .claude/rules/{topic}.md ({YYYY-MM-DD})` 마커 Edit 삽입

#### Step 1.5.3: 완료 메시지 후 조사 종료

```
🚀 {topic} 영구 룰로 격상
   포인터  : .claude/rules/{topic}.md
   본문    : .claude/rules/references/{topic}/
   다음 세션부터 자동 적용됩니다.
```

조사 자체는 종료 (이미 원칙이 알려진 문제이므로 재진단 불필요).
```

#### Step 6.3: Step 5 메시지 갱신 — 신규 저장 후 격상 안내

Edit, replace:

```
### 5. rules 파일 저장

`{project_root}/.hamstern/why/rules/` 디렉토리가 없으면 Bash로 생성합니다.
근본 원인 확정 시 `{project_root}/.hamstern/why/rules/{topic}.md` 에 저장합니다.
같은 토픽 파일이 있으면 새 원칙을 append합니다.
```

with:

```
### 5. rules 파일 저장

`{project_root}/.hamstern/why/rules/` 디렉토리가 없으면 Bash로 생성합니다.
근본 원인 확정 시 `{project_root}/.hamstern/why/rules/{topic}.md` 에 저장합니다.
같은 토픽 파일이 있으면 새 원칙을 append합니다.

저장 직후 다음 안내 메시지를 추가로 출력합니다 (사용자에게 격상 흐름을 알려주기 위함):

```
💡 이 원칙이 재발하면 /hams:why 가 자동으로 .claude/rules/ 로 격상을 제안합니다.
   지금 바로 격상하고 싶다면 /hams:rule promote {topic}
```
```

#### Step 6.4: Step 6 완료 메시지 갱신 — 격상 안내 추가

Edit, replace:

```
### 6. 완료 메시지

CLAUDE.md를 자동으로 수정하지 않습니다. 메시지만 출력합니다.

```
💾 규칙 저장: .hamstern/why/rules/{topic}.md
📋 CLAUDE.md에 추가하려면 해당 파일을 복사하세요.
```
```

with:

```
### 6. 완료 메시지

`.claude/rules/*.md` 가 자동 로드되므로 CLAUDE.md를 건드리지 않습니다.

```
💾 잠정 규칙 저장: .hamstern/why/rules/{topic}.md
💡 재발 시 자동으로 영구 룰 격상이 제안됩니다.
   수동 격상     : /hams:rule promote {topic}
   현재 룰 목록  : /hams:rule list
```
```

#### Step 6.5: 커밋

```bash
git add skills/why/SKILL.md
git commit -m "feat(why): add promotion mechanism for repeating rules (Step 1.5)"
```

---

### Task 7: marketplace.json 등록

**Files:**
- Modify: `.claude-plugin/marketplace.json`

`/hams:rule` 가 `/help` 와 자동완성에 노출되도록 skills 배열에 등록.

#### Step 7.1: 현재 파일 확인

(이미 컨텍스트에 있음 — `plugins[0].skills` 배열에 11개 항목)

#### Step 7.2: rule 항목 추가

Edit `.claude-plugin/marketplace.json`, replace:

```
        "./skills/why",
```

with:

```
        "./skills/why",
        "./skills/rule",
```

(why 바로 다음에 두는 이유: 두 스킬이 짝을 이루어 동작하므로 가독성)

#### Step 7.3: JSON 유효성 검증

```bash
python -c "import json; json.load(open('.claude-plugin/marketplace.json'))" && echo "valid JSON"
```

Expected: `valid JSON`

#### Step 7.4: 커밋

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat(rule): register /hams:rule in marketplace.json"
```

---

### Task 8: README.md 갱신

**Files:**
- Modify: `README.md`

신규 "Rules System" 섹션을 추가. 두 스킬을 하나의 시스템으로 설명.

#### Step 8.1: README 현재 구조 확인

```bash
grep -n "^## " README.md
```

기존 섹션 위치 파악.

#### Step 8.2: "Rules System" 섹션 작성 위치 결정

`/hams:why` 관련 기존 설명 섹션이 있으면 그 직후에 통합. 없으면 새 섹션을 적절한 위치(스킬 소개 섹션 그룹 안)에 삽입.

다음 패턴으로 grep해서 위치를 정한다:

```bash
grep -n "hams:why\|## /hams:" README.md
```

#### Step 8.3: 섹션 본문 작성

다음 내용을 README의 적절한 위치에 삽입:

````markdown
## Rules System (`/hams:why` + `/hams:rule`)

프로젝트의 반복되는 실수를 영구 원칙으로 전환하는 2단계 시스템.

### 메모리 위치 (Claude Code 기본 동작)

| 경로 | 자동 로드 | 용도 |
|------|----------|------|
| `.claude/rules/{topic}.md` | ✅ session_start (eager) | 포인터 (5~7줄, 항상 컨텍스트 보유) |
| `.claude/rules/references/{topic}/*.md,html` | ❌ lazy | 본문 (트리거 매칭 시 Claude가 능동적으로 Read) |
| `.hamstern/why/rules/{topic}.md` | ❌ | 잠정 보관소 (격상 전 단계) |

### 두 가지 등록 경로

#### 경로 1 — 진단형 `/hams:why`
1회차: 문제 진단 → `.hamstern/why/rules/` 잠정 저장.
2회차(같은 원칙 재발): 자동 격상 제안 → 승인 시 `.claude/rules/` 로 영구 이전.

```bash
/hams:why "테이블 헤더에서 검색·정렬 위치가 매번 다른 문제"
# → 근본 원인 분석 → 잠정 저장
# (나중에)
/hams:why "또 테이블 헤더 정렬이 좌측에 있어서 사용자 헤맴"
# → 매칭 → "격상하시겠습니까?" → 승인 → 영구 룰
```

#### 경로 2 — 직접 등록 `/hams:rule add`
사용자가 대화 중 도출한 패턴을 즉시 영구화. 진단 불확실성 우회.

```bash
# 패턴이 뚜렷한 작업을 끝낸 직후
/hams:rule add
# → 컨텍스트에서 자동 추출 → 1차 초안 → 검수 → .claude/rules/ 직행
```

### 룰 관리 명령

| 명령 | 동작 |
|------|------|
| `/hams:rule add` | 대화 컨텍스트에서 신규 룰 등록 |
| `/hams:rule list` | 현재 등록된 룰 목록 출력 |
| `/hams:rule edit {topic}` | 포인터 + references 표시 후 사용자 지시대로 수정 |
| `/hams:rule remove {topic}` | 룰 + references 폴더 전체 삭제 |
| `/hams:rule promote {topic}` | `.hamstern/why/rules/` 의 잠정 룰을 수동 격상 |

### 타입 분기 (코드 vs 디자인)

`/hams:rule add` 가 컨텍스트 키워드 휴리스틱으로 자동 판정:

- **코드 타입** → `examples.md` 만 생성 (코드 + 텍스트 다이어그램)
- **디자인 타입** → `examples.md` (JSX) + `mockup.html` (브라우저로 시각 확인)
- **둘 다** → 위 모두 생성

판정 결과는 1차 초안에 표시되며 사용자가 거부/변경 가능.

### 적용 범위 (paths)

격상·등록 시 두 가지 옵션:

- **전역** — 모든 작업에서 항상 컨텍스트에 로드
- **특정 경로** — `paths:` frontmatter 글로브 (예: `src/components/**`)로 매칭되는 경로 작업 시에만 lazy 로드

특정 경로 한정은 룰이 많아질 때 토큰 비용 관리에 유용.

### 파일 구조 예시

```
.claude/rules/
├── table-header-layout.md            # 포인터 (디자인 룰)
├── api-cache-first.md                # 포인터 (코드 룰)
└── references/
    ├── table-header-layout/
    │   ├── rule.md                   # 표면/근본 원인
    │   ├── examples.md               # JSX 코드
    │   ├── mockup.html               # 시각 확인용
    │   └── history.md                # 발견·재발 이력
    └── api-cache-first/
        ├── rule.md
        ├── examples.md
        └── history.md
```

### 설계 원칙

- **CLAUDE.md 절대 안 건드림** — `.claude/rules/*.md` 자동 로드 활용
- **포인터 작게, 본문은 lazy** — 토큰 부채 방지
- **사용자 확신 → 직접 등록, 진단 결과 → 격상 사다리** — 불확실성에 따른 분기

자세한 설계 배경: [`docs/discussions/2026-04-26-why-rule-promotion-design.md`](docs/discussions/2026-04-26-why-rule-promotion-design.md)
````

#### Step 8.4: 커밋

```bash
git add README.md
git commit -m "docs: add Rules System section (/hams:why + /hams:rule)"
```

---

### Task 9: 시나리오 검증 (수동 워크스루)

**Files:** (작성 없음 — 검증만)

스킬 markdown은 단위 테스트가 어렵다. 대신 Acceptance Criteria S1~S10을 사람이 직접 SKILL.md를 읽으며 멘탈 시뮬레이션.

#### Step 9.1: S1 (why 1회차) 검증

`skills/why/SKILL.md` 를 위에서 아래로 읽으며:
- [ ] Step 1 매칭 실패 시 정확히 Step 2로 진행하는가?
- [ ] Step 5 저장 후 격상 안내 메시지가 들어가 있는가?
- [ ] Step 6 완료 메시지에 `/hams:rule promote {topic}` 안내가 있는가?

#### Step 9.2: S2 (why 2회차 격상) 검증

- [ ] Step 1에서 `.claude/rules/` 와 `.hamstern/why/rules/` 두 곳 모두 확인하는가?
- [ ] Step 1.5 격상 제안 분기에서 `AskUserQuestion` 옵션 3개가 명확한가?
- [ ] 격상 실행 시 paths 질문이 누락되지 않는가?
- [ ] 원본에 `> 격상됨` 마커 삽입 단계가 있는가?

#### Step 9.3: S3 (rule add) 검증

`skills/rule/SKILL.md` §add 절을 읽으며:
- [ ] Step A0 마커 ON, Step A8 마커 OFF가 짝지어 있는가?
- [ ] Step A4 검수 루프 옵션 4개(진행/수정/타입변경/취소)가 명확한가?
- [ ] Step A7 파일 생성 5개(포인터, rule.md, examples.md, [mockup.html], history.md)가 빠짐없이 정의되어 있는가?
- [ ] Step A9 자가검증 항목들이 실제로 검증 가능한 형태인가?

#### Step 9.4: S4~S6 (list/edit/remove) 검증

- [ ] §list 가 `.claude/rules/*.md` glob을 사용하고 references/*.md 를 포함하지 않는가?
- [ ] §edit 가 mockup.html 도 표시 대상에 포함하는가?
- [ ] §remove 가 references 폴더 전체를 `rm -rf` 하는가?

#### Step 9.5: S7 (promote) 검증

- [ ] Step P4 (이미 격상됐는지) 검사가 있어 중복 격상 방지하는가?
- [ ] Step P8 마커 삽입 단계가 있는가?
- [ ] §add Step A7 과 동일한 파일 5개가 만들어지는가?

#### Step 9.6: S8 (타입 자동 판정) 검증

- [ ] §add Step A2 휴리스틱이 명확한 키워드 목록을 갖고 있는가?
- [ ] 디자인 타입일 때만 mockup.html 생성하는 분기가 Step A7에 있는가?

#### Step 9.7: S9 (마커 정리) 검증

- [ ] add, promote 가 모든 종료 경로(성공/취소/오류/검증실패)에서 `rm -f .hamstern/.deeptalk-running` 호출하는가?

#### Step 9.8: S10 (marketplace 등록) 검증

```bash
python -c "import json; m = json.load(open('.claude-plugin/marketplace.json')); print('rule' in [s.split('/')[-1] for s in m['plugins'][0]['skills']])"
```

Expected: `True`

#### Step 9.9: 발견된 이슈 정정

위 검증에서 누락·모순 발견 시 해당 Task로 돌아가 Edit으로 수정 후 추가 커밋:

```bash
git commit -m "fix(rule|why): {구체적 이슈} 수정"
```

#### Step 9.10: 검증 종료 커밋 (옵션 — 수정사항 있었을 때만)

수정이 있었다면 위 fix 커밋들로 끝. 없으면 커밋 생략.

---

### Task 10: 사용자 푸시 승인 + 푸시

**Files:** (없음 — git 작업만)

#### Step 10.1: 변경사항 요약 출력

```bash
git log --oneline origin/main..HEAD
```

Expected: Task 1~9 동안 만들어진 6~10개 커밋 목록.

```bash
git diff --stat origin/main..HEAD
```

Expected: skills/rule/, skills/why/SKILL.md, .claude-plugin/marketplace.json, README.md, docs/{discussions,plans}/* 변경 통계.

#### Step 10.2: 사용자 명시 승인 받기

다음 메시지 출력 후 사용자 응답 대기:

```
✅ 구현 완료. 다음 변경사항을 origin/main 으로 푸시할까요?

  - skills/rule/ 신규 (SKILL.md + 5개 템플릿)
  - skills/why/SKILL.md 격상 메커니즘 추가
  - .claude-plugin/marketplace.json 갱신
  - README.md "Rules System" 섹션 추가
  - docs/discussions/, docs/plans/ 신규

푸시하시겠습니까? (yes / no / 먼저 변경사항 확인)
```

**중요:** 사용자가 명시적으로 `yes` 응답 전에는 `git push` 절대 실행 금지. 거부 시 로컬 커밋만 유지하고 종료.

#### Step 10.3: 승인 시 푸시

```bash
git push origin main
```

#### Step 10.4: 완료 메시지

```
🚀 푸시 완료
   브랜치 : main
   커밋   : {N}건
   다음   : 사용자가 새 세션을 시작하면 /hams:rule, 갱신된 /hams:why 즉시 사용 가능
```

---

## Self-Review Checklist (작성자 자체 점검)

플랜 작성 후 다음을 확인하고 발견된 이슈는 인라인으로 수정:

- [x] **Spec coverage**: Acceptance Criteria S1~S10 각 항목이 적어도 하나의 Task에서 다뤄지는가?
  - S1, S2 → Task 6 (why 갱신)
  - S3, S8, S9 → Task 3 (rule add)
  - S4, S5, S6 → Task 4 (list/edit/remove)
  - S7 → Task 5 (promote)
  - S10 → Task 7 (marketplace)
  - 검증 → Task 9
- [x] **Placeholder scan**: "TBD", "TODO", "implement later" 없음. 모든 Step 에 구체 명령/내용 포함.
- [x] **Type consistency**: `topic`, `paths frontmatter`, 템플릿 플레이스홀더 이름이 Task 1~6에서 동일하게 사용됨.
- [x] **Templates → Tasks 의존**: Task 3, 5, 6 가 Task 1 템플릿 사용. Task 1을 먼저 구현해야 후속 작업이 가능 — 순서 유지.
- [x] **Common Mistakes 섹션**: rule SKILL.md 에 8가지 함정 작성 (Task 5).
- [x] **why SKILL.md 의 Step 1.5.2 가 promote Step P5~P10 와 동일 작업 수행**: 두 곳에 중복 명세하지 않고, why 측에서 promote 절을 참조하는 형태로 작성됨. 단, 인라인 실행이라 명시.

---

## Execution Notes

- **TDD 적용 안 됨**: 산출물이 markdown 스킬 콘텐츠라 RED→GREEN 사이클 부적합. 대신 Task 9 시나리오 워크스루로 검증.
- **워크트리 미사용**: 사용자가 단일 브랜치 워크플로우 선호. 직접 main에서 작업.
- **푸시는 사용자 명시 승인 후**: Task 10에서 반드시 확인.
- **이 플랜 자체도 docs/plans/에 커밋됨**: Task 1 시작 전에 현재 상태(plan + discussion)를 한 번 커밋해두면 깔끔.

  ```bash
  git add docs/discussions/ docs/plans/
  git commit -m "docs: add design discussion and implementation plan for /hams:rule + /hams:why promotion"
  ```
