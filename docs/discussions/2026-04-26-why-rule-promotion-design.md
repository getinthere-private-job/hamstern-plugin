# /hams:why 격상 메커니즘 + /hams:rule 신규 스킬 설계

- 날짜: 2026-04-26
- 참여: 사용자 (ssarmango@gmail.com) + Claude (Opus 4.7, deeptalk 모드)

## 배경

기존 `/hams:why` 는 근본 원인을 발견하고 `.hamstern/why/rules/{topic}.md` 에 저장하지만, 같은 문제가 재발해도 자동으로 영구 룰로 격상되지 않았다. 사용자 요구: "같은 실수가 두 번 일어나면 그 원칙을 프로젝트의 영구 자산으로 만들고, 이후 자동으로 적용되어 동일 실수를 막고 싶다."

또한 사용자가 직접 룰을 추가하는 경로(why 진단 흐름을 거치지 않고 명시적으로 룰을 등록하는 워크플로우)가 없다는 지적.

## 핵심 논의

### 1. `.claude/rules/` 자동 로드 메커니즘 검증

초기에 Claude가 "`.claude/rules/*.md` 는 자동 로드되지 않으므로 CLAUDE.md 에 `@import` 가 필요하다"고 주장. 사용자가 검증 요청 → context7 으로 공식 문서(`/anthropics/claude-code`, `/ericbuess/claude-code-docs`) 조회 결과:

- `.claude/rules/*.md` 는 **session_start 에 eager-load** 되는 1급 메모리 위치
- `InstructionsLoaded` hook 이 `CLAUDE.md or .claude/rules/*.md` 로딩 시 발화 — 공식 명시
- `paths:` frontmatter 로 lazy-load (path-glob 매칭) 도 가능

→ Claude의 초기 주장은 사실관계 오류. 사용자가 옳았으며 **CLAUDE.md 는 평생 건드릴 필요 없음**.

### 2. 토큰 노이즈 문제 → 2-tier 구조

모든 룰이 매 세션 컨텍스트에 영구 로드되면 룰이 누적될수록 토큰 부채가 됨. 해결책: **작은 포인터 + 별도 references 폴더**.

- `.claude/rules/{topic}.md` (포인터, 5~7줄, 항상 로드)
- `.claude/rules/references/{topic}/` (본문, lazy — 자동 로드 안 됨, Claude가 트리거 매칭 시 능동적으로 Read)

`references/` 가 자동 로드 안 되는 이유: 공식 문서가 자동 로드 명시한 패턴은 `.claude/rules/*.md` 직속 파일뿐. 하위 폴더는 해당 안 됨.

### 3. `/hams:rule` 멀티 명령 신설

사용자가 직접 룰을 등록하는 워크플로우는 why(진단형)와 본질적으로 다름 — 사용자가 이미 확신 상태이므로 `.hamstern/why/rules/` 격리 단계 불필요, 바로 `.claude/rules/` 로.

`/hams:rule add` 는 **skill-creator 스타일** — 현재 대화 컨텍스트에서 자동 추출(원칙·트리거·코드/디자인 결과물·타입), 1차 초안 제시, 1~2회 검수, 승인 → 파일 생성.

### 4. 타입 분기 (코드 vs 디자인)

- **코드 타입**: `examples.md` 에 코드 + 텍스트 다이어그램
- **디자인 타입**: `examples.md` (JSX) + **`mockup.html`** (브라우저로 열어 시각 확인)
- 타입은 키워드 휴리스틱으로 자동 판정 + 1차 초안에 표시 → 사용자가 거부/수정 가능

### 5. 격상 사다리

- 1회차 why → `.hamstern/why/rules/{topic}.md` 저장 + "재발 시 격상 제안" 안내 메시지
- N회차 why (매칭) → "격상하시겠습니까?" → 승인 시:
  - `.claude/rules/{topic}.md` (포인터) 생성
  - `.claude/rules/references/{topic}/` 생성 (rule.md, examples.md, history.md, [선택] mockup.html)
  - 원본 `.hamstern/why/rules/{topic}.md` 맨 위에 `> 격상됨 → .claude/rules/{topic}.md (날짜)` 마커 추가
  - 격상 시 paths 글로브 사용자 선택 (전역 vs 특정 경로)
- hits/카운터 없음 — 1회 매칭이면 바로 제안

## 결론

### 스킬 생태계 (확정)

```
/hams:why                  - 증상 진단, 근본 원인 발견 (.hamstern/why/rules/ 잠정)
/hams:why (재발 매칭 시)    - .claude/rules/ 격상 제안
/hams:rule add             - 대화 컨텍스트에서 자동 추출, 직접 .claude/rules/ 생성
/hams:rule list            - 현재 룰 목록
/hams:rule edit {topic}    - 특정 룰 수정
/hams:rule remove {topic}  - 룰 + references 폴더 제거
/hams:rule promote {topic} - .hamstern/why/rules/ 에서 수동 격상
```

### 파일 구조 (확정)

```
.claude/rules/
├── {topic}.md            ← 포인터 (5~7줄, 항상 로드)
└── references/
    └── {topic}/
        ├── rule.md       ← 표면/근본 원인, 추론 (lazy)
        ├── examples.md   ← 코드 ✅/❌ 패턴 (lazy)
        ├── mockup.html   ← (디자인 타입만) HTML mockup (lazy)
        └── history.md    ← 발견·재발 이력 (lazy)
```

### 포인터 파일 형식

```markdown
## {원칙명}

**원칙:** {한 문장}
**적용 트리거:** {언제 발동되는지 — 키워드/도메인}
**자세히 (트리거 매칭 시 순서대로 읽기):**
  1. references/{topic}/rule.md
  2. references/{topic}/mockup.html  (디자인 타입만)
  3. references/{topic}/examples.md
```

(선택) `paths:` frontmatter 로 path-glob 한정 가능.

### 핵심 원칙

- CLAUDE.md 평생 안 건드림 — `.claude/rules/*.md` 자동 로드 활용
- 사용자 확신 → 격상 사다리 우회 (`/hams:rule add` 직행)
- 진단 결과 → 사다리 통과 (`.hamstern` 격리 후 재발 시 격상)
- 토큰 비용 최소화 — 포인터만 항상 로드, 본문은 lazy

## 다음 단계

1. **deeptalk 종료, writing-plans 스킬로 전환** — 구현 플랜 작성
2. **구현 항목**:
   - `/hams:why` SKILL.md 갱신 (격상 메커니즘 추가)
   - `/hams:rule` 신규 스킬 (멀티 서브커맨드)
   - 포인터 / references 템플릿 정리
   - 코드 vs 디자인 타입 자동 판정 휴리스틱
   - mockup.html 생성 로직
3. **README 갱신** — 두 스킬 사용법, 격상 흐름, 파일 구조
4. **플러그인 푸시** (사용자 명시 승인 후)
