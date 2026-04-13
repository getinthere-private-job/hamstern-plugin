---
name: hams-registry-collector
description: Claude Code 스킬/플러그인 레지스트리 수집 (큐레이션 소스)
---

# Registry Collector

GitHub의 다양한 소스에서 Claude Code 스킬/플러그인을 수집하여 `~/.hamstern/skills-registry.json`을 생성합니다.

이 데이터는 `/hams-skill-picker`에서 스킬 추천 시 참고됩니다.

## 동작

```bash
/hams-registry-collector
```

**특징:**
- 매번 호출할 때마다 새로 수집 (캐시 없음)
- 증분 업데이트: 새로 수집한 것과 기존 registry 병합
- 중복 제거 (id 기준)

## 수집 소스

| 우선순위 | 소스 | 규모 | 설명 |
|---------|------|------|------|
| 1 | `anthropics/claude-plugins-official` | ~수십개 | Anthropic 공식 플러그인 — 가장 신뢰도 높음 |
| 2 | `anthropics/claude-plugins-community` | ~수백개 | 커뮤니티 검수 통과 플러그인 (매일 동기화) |
| 3 | `hesreallyhim/awesome-claude-code` | ~190개 | 큐레이션된 스킬/에이전트/플러그인 리스트 |
| 4 | GitHub topic `claude-code-plugin` | 최대 1,000개 | 토픽 태그 기반 — 스타순 정렬 |
| 5 | GitHub topic `claude-code` (스타 필터) | 최대 1,000개 | 광범위 검색 — gstack, everything-claude-code 포함 |
| 6 | `glama.ai` MCP | ~10개 | 인기 MCP 서버 (상위 30개 중 우선순위) |

## 개수 제한

GitHub Search API는 **쿼리당 최대 1,000개** 결과를 반환합니다 (GitHub 정책).

| 상황 | 제한 |
|------|------|
| 토픽 검색 결과 | 최대 1,000개 (스타순 정렬 → 인기 플러그인 우선 수집) |
| API 호출 (인증 없음) | 분당 10회, 시간당 60회 |
| API 호출 (GITHUB_TOKEN) | 분당 30회, 시간당 5,000회 |

→ `claude-code-plugin` 태그 레포 1,528개 중 상위 1,000개만 수집됨.
→ `claude-code` 태그 레포 17,999개 중 스타 상위 1,000개만 수집됨 (gstack 71k⭐, everything-claude-code 153k⭐ 등 포함).

## 수집된 데이터 예

```
🔄 Collecting skill registry from curated sources...

🏛️  anthropics/claude-plugins-official 수집...
   ✓ Added 12 official plugins
🌐 anthropics/claude-plugins-community 수집...
   ✓ Added 84 community plugins
📚 awesome-claude-code 수집...
   ✓ Added 190 awesome skills
🔍 GitHub topic:claude-code-plugin 수집...
   ✓ Added 1000 plugins (1,528개 중 스타 상위)
🔍 GitHub topic:claude-code 수집...
   ✓ Added 1000 plugins (17,999개 중 스타 상위)
🤖 glama.ai MCP 서버 수집...
   ✓ Added 10 MCP servers

✅ Registry updated: ~/.hamstern/skills-registry.json

📊 Total: 2,124개 (중복 제거 후)
   ├─ official: 12
   ├─ community: 84
   ├─ awesome: 190
   ├─ github-plugin: 1,000
   ├─ github-topic: 1,000
   └─ mcp: 10
```

## 출력 형식

```json
[
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
  },
  ...
]
```

## 메타데이터 필드

- `id` — 스킬 식별자 (provider:slug)
- `provider` — 제공자 (official, community, awesome, github-plugin, github-topic, mcp)
- `name` — 스킬/플러그인 이름
- `description` — 한 줄 설명
- `category` — 카테고리 (engineering-workflow, testing, debugging, deployment 등)
- `icon` — 이모지
- `github_repo` — GitHub 저장소 (owner/repo)
- `github_stars` — GitHub 스타 수
- `popularity_score` — 인기도 점수 (0.0~1.0, 스타수 기반 정규화)
- `install_command` — 설치 명령어 (README 파싱, 없으면 null)

## 저장 위치

```
~/.hamstern/skills-registry.json
```

## 기술 상세

### 데이터 소스별 수집 방법

**anthropics/claude-plugins-official**
- `https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/plugins/` 디렉토리 파싱
- 인증 불필요

**anthropics/claude-plugins-community**
- `https://raw.githubusercontent.com/anthropics/claude-plugins-community/main/plugins/` 디렉토리 파싱
- 인증 불필요

**awesome-claude-code (hesreallyhim)**
- README.md raw 다운로드
- 마크다운 링크 파싱: `- [name](url) - description`

**GitHub topic 검색**
- `https://api.github.com/search/repositories?q=topic:claude-code-plugin&sort=stars&per_page=100`
- `https://api.github.com/search/repositories?q=topic:claude-code&sort=stars&per_page=100&min_stars=100`
- GITHUB_TOKEN 있으면 속도 향상 (선택)

**glama.ai MCP Servers**
- `https://glama.ai/api/mcp/v1/servers?sort=popularity&limit=30`
- 인증 불필요

### 성능

- 전체 수집: ~15초 (6개 소스 순차 호출)
- GITHUB_TOKEN 있으면 병렬 처리 가능 → ~8초

### GITHUB_TOKEN (선택)

환경변수 `GITHUB_TOKEN` 설정 시:
- API 호출 한도 시간당 5,000회 (미설정: 60회)
- 없어도 동작하지만 rate limit 걸릴 수 있음

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

---

## 주의사항

- 인터넷 연결 필수
- GitHub API 1,000개 결과 한도는 우회 불가 (GitHub 정책)
- 스타 수 낮은 소규모 플러그인은 수집 안 될 수 있음

## 팁

- GITHUB_TOKEN 설정하면 더 빠르고 안정적
- `/hams-skill-picker`와 함께 사용하면 프로젝트에 필요한 스킬을 빠르게 찾을 수 있음
- registry.json은 버전 관리 대상 아님 (자동 생성)
