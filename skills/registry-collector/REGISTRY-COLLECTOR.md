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

GitHub Search API는 **쿼리당 최대 1,000개** 결과를 반환합니다 (GitHub 정책, 우회 불가).

| 상황 | 제한 |
|------|------|
| 검색 결과 | 최대 1,000개/쿼리 → 스타순 정렬로 인기 플러그인 우선 수집 |
| API 호출 (인증 없음) | 분당 10회, 시간당 60회 |
| API 호출 (GITHUB_TOKEN) | 분당 30회, 시간당 5,000회 |

→ 스타 수 낮은 소규모 플러그인은 수집 안 될 수 있음.
→ gstack (71k⭐), everything-claude-code (153k⭐) 등 인기 플러그인은 항상 포함됨.

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
    "popularity_score": 0.85
  },
  {
    "id": "github-topic:gstack",
    "provider": "github-topic",
    "name": "gstack",
    "description": "23 opinionated tools serving as CEO, Designer, Eng Manager, Release Manager",
    "category": "engineering-workflow",
    "icon": "🚀",
    "github_repo": "garrytan/gstack",
    "github_stars": 71200,
    "popularity_score": 1.0
  }
]
```

## 메타데이터 필드

- `id` — 스킬 식별자 (provider:slug)
- `provider` — 제공자 (official, community, awesome, github-plugin, github-topic, mcp)
- `name` — 플러그인/스킬 이름
- `description` — 한 줄 설명
- `category` — 카테고리 (engineering-workflow, testing, debugging, deployment 등)
- `icon` — 이모지
- `github_repo` — GitHub 저장소 (owner/repo)
- `github_stars` — GitHub 스타 수
- `popularity_score` — 인기도 점수 (0.0~1.0, 스타수 기반 정규화)

## 증분 업데이트

매번 호출할 때마다:
1. 각 소스에서 최신 데이터 수집
2. 기존 registry와 병합
3. id 기준으로 중복 제거 (새 데이터가 우선)
4. 결과를 registry.json에 저장

## 저장 위치

```
~/.hamstern/skills-registry.json
```

---

## 기술 상세

### 데이터 소스별 수집 방법

**anthropics/claude-plugins-official**
- `https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/plugins/` 디렉토리 파싱
- 인증 불필요

**anthropics/claude-plugins-community**
- `https://raw.githubusercontent.com/anthropics/claude-plugins-community/main/plugins/` 디렉토리 파싱
- 인증 불필요

**awesome-claude-code (hesreallyhim)**
- `https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/README.md` raw 다운로드
- 마크다운 링크 파싱: `- [name](url) - description`

**GitHub topic:claude-code-plugin**
```
GET https://api.github.com/search/repositories
  ?q=topic:claude-code-plugin
  &sort=stars&order=desc
  &per_page=100
  (10페이지 = 최대 1,000개)
```

**GitHub topic:claude-code (스타 필터)**
```
GET https://api.github.com/search/repositories
  ?q=topic:claude-code+stars:>50
  &sort=stars&order=desc
  &per_page=100
  (10페이지 = 최대 1,000개)
```

**glama.ai MCP Servers**
```
GET https://glama.ai/api/mcp/v1/servers?sort=popularity&limit=30
```

### GITHUB_TOKEN (선택)

환경변수 `GITHUB_TOKEN` 설정 시:
- 시간당 5,000회 (미설정: 60회)
- 없어도 동작하지만 GitHub topic 수집 시 rate limit 걸릴 수 있음

```bash
export GITHUB_TOKEN=ghp_xxxx
/hams-registry-collector
```

### 성능

| 설정 | 예상 소요시간 |
|------|-------------|
| GITHUB_TOKEN 없음 | ~30초 (rate limit 회피를 위한 지연 포함) |
| GITHUB_TOKEN 있음 | ~15초 |

---

## 사용 사례

### 1. 수동 업데이트

```bash
/hams-registry-collector
/hams-skill-picker  # registry 참고해서 추천
```

### 2. 자동화 (선택)

```bash
/schedule "0 9 * * MON" /hams-registry-collector
```

### 3. GITHUB_TOKEN 설정 후 실행

```bash
export GITHUB_TOKEN=ghp_xxxx
/hams-registry-collector
```

---

## 주의사항

- 인터넷 연결 필수
- GitHub Search API 1,000개 한도는 GitHub 정책으로 우회 불가
- GITHUB_TOKEN 없으면 GitHub 수집 중 rate limit 발생 가능 (자동 재시도)
- glama.ai API 다운 시 MCP 수집 실패 → 나머지 소스는 정상 수집
