# registry-collector install_command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** registry-collector가 GitHub README에서 `install_command`를 파싱하여 수집하고, skill-picker가 이를 우선 사용하도록 한다.

**Architecture:** `skills/registry-collector/SKILL.md`에 README 파싱 로직을 추가하고, `skills/skill-picker/SKILL.md`의 설치 커맨드 생성 규칙을 `install_command` 필드 우선으로 수정한다.

**Tech Stack:** Markdown (SKILL.md), JSON (skills-registry.json 스키마 변경)

---

### Task 1: registry-collector SKILL.md — install_command 수집 추가

**Files:**
- Modify: `skills/registry-collector/SKILL.md`

- [ ] **Step 1: `## 출력 형식` 섹션의 스키마에 `install_command` 필드 추가**

현재:
```json
{
  "id": "official:superpowers",
  "provider": "official",
  "name": "Superpowers",
  "description": "Bundle of core competencies for software engineering",
  "category": "engineering-workflow",
  "icon": "⚡",
  "github_repo": "obra/superpowers",
  "github_stars": 5420,
  "popularity_score": 0.85
}
```

수정 후:
```json
{
  "id": "official:superpowers",
  "provider": "official",
  "name": "Superpowers",
  "description": "Bundle of core competencies for software engineering",
  "category": "engineering-workflow",
  "icon": "⚡",
  "github_repo": "obra/superpowers",
  "github_stars": 5420,
  "popularity_score": 0.85,
  "install_command": "/plugin marketplace add obra/superpowers"
}
```

- [ ] **Step 2: `## 메타데이터 필드` 섹션에 `install_command` 항목 추가**

현재 목록 마지막에 추가:
```
- `install_command` — 설치 명령어 (README 파싱, 없으면 null)
```

- [ ] **Step 3: `## 기술 상세` 섹션에 `install_command` 파싱 방법 추가**

`### install_command 감지` 섹션을 추가합니다:

```markdown
### install_command 감지

수집 시 각 레포의 README.md를 다운로드하여 설치 명령어를 파싱합니다.
**stars > 100 인 레포만 적용** (rate limit 절약).

우선순위 순서로 감지:

| 우선순위 | 패턴 | 예시 |
|---------|------|------|
| 1 | `/plugin marketplace add {repo}` | `/plugin marketplace add obra/superpowers` |
| 2 | `npx {package}@latest` | `npx get-shit-done-cc@latest` |
| 3 | `npm install -g {package}` | `npm install -g some-tool` |
| 4 | `npm install {package}` | `npm install some-package` |

감지 실패 시 `install_command: null`.
README 다운로드 실패 시에도 `null` 처리 후 계속 진행.
```

- [ ] **Step 4: 커밋**

```bash
git add skills/registry-collector/SKILL.md
git commit -m "feat: registry-collector install_command 수집 추가"
```

---

### Task 2: skill-picker SKILL.md — install_command 우선 사용

**Files:**
- Modify: `skills/skill-picker/SKILL.md`

- [ ] **Step 1: `## 설치 커맨드 생성 규칙` 섹션 수정**

현재:
```markdown
## 설치 커맨드 생성 규칙

- registry에 `github_repo` 있으면: `/plugin marketplace add {github_repo}` + `/plugin install {name}`
- `claude-plugins-official` 마켓플레이스 플러그인이면: `/plugin install {name}@claude-plugins-official`
- 정보 없으면: `/plugin marketplace add {github_repo}` 만 안내
```

수정 후:
```markdown
## 설치 커맨드 생성 규칙

1. registry에 `install_command` 있으면: 그대로 사용
2. `install_command`가 null이고 `github_repo` 있으면: `/plugin marketplace add {github_repo}` + `/plugin install {name}`
3. `claude-plugins-official` 마켓플레이스 플러그인이면: `/plugin install {name}@claude-plugins-official`
4. 정보 없으면: 설치 방법 불명확 안내
```

- [ ] **Step 2: 커밋**

```bash
git add skills/skill-picker/SKILL.md
git commit -m "feat: skill-picker install_command 필드 우선 사용"
```

---

### Task 3: 수동 검증

**Files:** 없음 (확인만)

- [ ] **Step 1: `/hams-registry-collector` 재실행**

```
/hams-registry-collector
```

get-shit-done 항목에 `install_command: "npx get-shit-done-cc@latest"` 가 포함됐는지 확인:
```bash
python -c "import json; d=json.load(open(r'~/.hamstern/skills-registry.json')); [print(x) for x in d if 'get-shit-done' in x.get('id','')]"
```

- [ ] **Step 2: `/hams-skill-picker` 에서 get-shit-done 추천 확인**

```
/hams-skill-picker
"spec-driven 개발 워크플로우가 필요해"
```

기대 결과: get-shit-done 추천 시 설치 커맨드가 `npx get-shit-done-cc@latest`로 표시됨.
