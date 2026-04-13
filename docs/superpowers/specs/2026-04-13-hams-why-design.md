# hams-why 스킬 디자인

**날짜:** 2026-04-13

## 개요

`/hams-why "문제 설명"` 은 어떤 현상의 근본 원인을 소크라테스식으로 파고드는 스킬입니다.
4개의 서브에이전트가 가설을 병렬 검증하고, Claude가 스스로 코드/파일을 추적하며 표면 원인에서 원칙 수준의 근본 원인까지 도달합니다.
발견한 원칙은 `{project_root}/.hamstern/why/rules/` 에 저장되며, 사용자가 원하면 CLAUDE.md로 옮깁니다.

## 스킬 메타데이터

- **name:** `hams-why`
- **커맨드:** `/hams-why`
- **위치:** `skills/why/SKILL.md`
- **allowed-tools:** Read, Glob, Grep, Bash, Agent

## 동작 흐름

### 1단계: 가설 생성

문제 설명을 받으면 가능한 원인 가설 3-5개를 생성합니다.
각 가설에 예상 확률(%)을 표시합니다.

```
H1 (40%) registry에 install_command 필드 없음
H2 (30%) skill-picker의 설치 커맨드 생성 로직이 npm 패키지를 못 구분
H3 (20%) registry-collector가 해당 레포를 잘못 파싱
H4 (10%) 레포 이름과 npm 패키지명이 다름
```

### 2단계: 서브에이전트 병렬 조사

가설 수에 맞춰 최대 4개의 서브에이전트를 병렬 실행합니다.
각 에이전트는 해당 가설을 코드/파일/데이터로 검증하고 결과를 보고합니다.

### 3단계: 소크라테스식 자기 추론

서브에이전트 결과를 취합한 후 Claude가 스스로 "왜?" 를 반복하며 근본 원인까지 파고듭니다.
**사용자에게 묻지 않습니다.** 코드와 파일로 추적합니다.

단, 코드/파일만으로 파악 불가능한 경우(의도, 기획 배경 등)에는 사용자에게 묻습니다.

**예시:**
```
서브에이전트 결과: "margin: 20 하드코딩 발견"

[Claude 내부 추론]
"왜 margin: 20인가?" → 코드 추적 → 정렬 기준 없이 임의 입력
"왜 정렬 기준이 없는가?" → 파일 탐색 → 레이아웃 규칙 정의 없음
→ 근본 원인: 정렬 기준선 없이 눈대중으로 배치
```

표면 원인(여백 20 제거)이 아니라 **원칙 수준**(정렬 기준 부재)에서 멈춥니다.

### 4단계: rules 파일 저장

근본 원인이 확정되면 `{project_root}/.hamstern/why/rules/{topic}.md` 에 저장합니다.

**파일 형식:**
```markdown
## [원칙명]
**발견:** 2026-04-13
**트리거:** 여백을 임의값으로 맞춤
**표면 원인:** margin: 20 하드코딩
**근본 원인:** 정렬 기준선 없이 눈대중으로 배치
**원칙:** 모든 UI 요소는 그리드/정렬 기준에 맞춰 배치한다
```

토픽이 같은 원칙은 같은 파일에 append합니다.

### 5단계: CLAUDE.md 안내

```
💾 규칙 저장: .hamstern/why/rules/ui-alignment.md
📋 CLAUDE.md에 추가하려면 해당 파일을 복사하세요.
```

실행은 사용자 몫입니다. 스킬이 직접 CLAUDE.md를 수정하지 않습니다.

## 기존 rules 재사용

`/hams-why` 실행 시 기존 rules 파일이 있으면 먼저 읽어 패턴 매칭을 시도합니다.
유사한 원칙이 이미 있으면 새 조사 없이 해당 원칙을 참조합니다.

## 범위

- 코드, 설정 파일, 스킬 데이터 등 모든 파일 대상
- hamstern 에코시스템 전용이 아닌 범용 원인 파악
- rules는 프로젝트별 (`{project_root}/.hamstern/why/rules/`)

---

# registry-collector install_command 수집 디자인

## 개요

registry-collector가 각 GitHub 레포의 README를 파싱하여 `install_command` 필드를 수집합니다.
skill-picker가 설치 커맨드를 github_repo에서 추정하는 대신 정확한 명령어를 사용할 수 있게 됩니다.

## install_command 감지 패턴

우선순위 순서로 탐지합니다:

| 우선순위 | 패턴 | 예시 |
|---------|------|------|
| 1 | `/plugin marketplace add {repo}` | `/plugin marketplace add obra/superpowers` |
| 2 | `npx {package}@latest` | `npx get-shit-done-cc@latest` |
| 3 | `npm install -g {package}` | `npm install -g some-tool` |
| 4 | `npm install {package}` | `npm install some-package` |

감지 실패 시 `install_command: null` — skill-picker가 기존 fallback 사용.

## 스키마 변경

```json
{
  "id": "github-plugin:get-shit-done",
  "github_repo": "qrdl/get-shit-done",
  "install_command": "npx get-shit-done-cc@latest",
  ...
}
```

## 성능 고려

README 파싱은 기존 수집에 추가 HTTP 요청이 필요합니다.
- GitHub API rate limit 고려: GITHUB_TOKEN 없으면 시간당 60회
- 상위 인기 레포 위주로만 적용 (stars > 100)
- 실패 시 `null` 처리 후 계속 진행
