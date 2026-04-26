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

호출 즉시 다음 단계를 순서대로 수행한다.

### Step A0: deep-talk 마커 ON

```bash
mkdir -p .hamstern && touch .hamstern/.deeptalk-running
```

`.hamstern/` 미존재 프로젝트면 건너뜀. 모든 종료 경로(성공/취소/오류/검증실패)에서 `rm -f` 필수.

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

컨텍스트가 비어 있어 위 정보를 추출할 수 없으면, 폴백:
> "최근 대화에서 패턴을 추출할 수 없습니다. 어떤 원칙을 등록할지 직접 알려주세요."
이후 사용자가 자유 텍스트로 원칙·트리거·예시를 제공 → Step A3로 진행.

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

각 파일 생성 (Read로 템플릿 읽고, 플레이스홀더 치환 후 Write):

#### 1. 포인터 `.claude/rules/{topic}.md`

`./templates/pointer.md` 읽기. 다음 플레이스홀더 치환:

- `{{paths_frontmatter}}` →
  - 전역이면 빈 문자열 `""`
  - 특정 경로면 다음 (마지막 빈 줄 1개 포함):
    ```
    ---
    paths:
      - "src/components/**"
    ---
    
    ```
  - 글로브 여러 개면 `paths:` 아래에 `  - "..."` 라인 여러 개.
- `{{title}}` → 한국어 원칙명
- `{{principle}}` → 한 문장 원칙
- `{{trigger}}` → 트리거 텍스트
- `{{references_list}}` → 단일 다중 라인 블록. 타입에 따라:
  - **코드 타입**:
    ```
      1. references/{topic}/rule.md
      2. references/{topic}/examples.md
    ```
    (`{topic}` 도 실제 값으로 치환)
  - **디자인 타입 또는 둘 다**:
    ```
      1. references/{topic}/rule.md
      2. references/{topic}/mockup.html
      3. references/{topic}/examples.md
    ```

치환 완료 후 Write.

#### 2. rule.md `.claude/rules/references/{topic}/rule.md`

`./templates/rule.md` 읽기. 치환:

- `{{title}}` → 한국어 원칙명
- `{{date}}` → 시스템 오늘 날짜 (`date +%F` 결과 또는 YYYY-MM-DD)
- `{{trigger_context}}` → Step A1에서 도출한 작업 도메인 한 줄 (예: "ProjectsTable.tsx 헤더 작업 중")
- `{{surface_cause}}` → 표면 증상 (사용자 강조 표현 그대로)
- `{{root_cause}}` → 원칙 수준 원인 (Claude 추론)
- `{{principle}}` → 한 문장 원칙
- `{{rationale}}` → 사용자가 언급한 근거 (없으면 비움 — 빈 문자열로 치환, 헤딩 `## 근거`는 유지)

치환 후 Write.

#### 3. examples.md `.claude/rules/references/{topic}/examples.md`

`./templates/examples.md` 읽기. 치환:

- `{{title}}` → 원칙명
- `{{lang}}` → 코드 추출에서 추론 (`tsx`, `ts`, `py`, `java`, …)
- `{{good_example}}` → 컨텍스트에서 도출한 올바른 패턴 코드
- `{{bad_example}}` → 잘못된 패턴 코드 (없으면 빈 문자열로 치환 → 헤딩과 코드 펜스가 빈 블록으로 남되 markdown은 깨지지 않음)
- `{{flow_section}}` → 코드 타입에서 흐름 다이어그램 있으면 다음 형태 문자열, 없으면 `""`:
  ```
  ## 흐름 (텍스트 다이어그램)
  
      요청 → 검증 → 처리 → 응답
  ```
- `{{found_in_section}}` → 다음 한 줄로 시작 (등록 시점 표기):
  ```
  ## 발견된 실제 사례
  - {파일경로} ({YYYY-MM-DD}) — 등록 시점
  ```
  파일경로는 컨텍스트에서 도출한 작업 도메인의 대표 파일 (예: `src/components/ProjectsTable.tsx`).

치환 후 Write.

#### 4. mockup.html `.claude/rules/references/{topic}/mockup.html` (디자인/둘 다 타입에만)

`./templates/mockup.html` 읽기. 치환:

- `{{title}}` → 원칙명
- `{{principle}}` → 원칙 한 문장
- `{{custom_css}}` → 룰별 CSS (필요 시 — 예: `.table-header { display: flex; justify-content: space-between; }`). 필요 없으면 빈 문자열.
  - **주의**: 사용자 제공 CSS에 `</style>` 시퀀스가 있으면 반드시 제거하거나 escape (HTML 안전성).
- `{{good_html}}` → 컨텍스트의 좋은 HTML 마크업
- `{{bad_html}}` → 잘못된 HTML 마크업 (없으면 빈 문자열)

치환 후 Write.

코드 타입이면 mockup.html을 만들지 않는다.

#### 5. history.md `.claude/rules/references/{topic}/history.md`

`./templates/history.md` 읽기. 치환:

- `{{title}}` → 원칙명
- `{{date}}` → YYYY-MM-DD
- `{{registration_path}}` → `"/hams:rule add (수동 등록)"`
- `{{discovery_log}}` → 한 줄 (등록 시점 진입):
  ```
  - **{date}** — {file_or_context}: 등록 시점 1차 패턴 도출
  ```
- `{{recurrence_log}}` → `(아직 없음)`

치환 후 Write.

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
- `.claude/rules/{topic}.md` 가 5~10줄 사이인가? (포인터는 짧아야 함. paths frontmatter 포함 시 약간 더 길 수 있음)
- 디자인/둘 다 타입이면 `mockup.html` 이 실제로 존재하는가? (`test -f`)
- `references/{topic}/` 안에 `rule.md`, `examples.md`, `history.md` 가 있는가?
- 포인터의 frontmatter 가 paths 옵션 선택과 일치하는가? (전역이면 frontmatter 없음, 특정 경로면 `paths:` 항목 존재)
- 포인터의 `{{references_list}}` 가 코드 타입이면 2단계, 디자인/둘 다 타입이면 3단계 번호인가?

검증 실패 시 사용자에게 어떤 검증이 실패했는지 보고 + 작성한 파일 경로를 알려주고 마커 OFF 후 종료 (수동 정정 가능).

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
