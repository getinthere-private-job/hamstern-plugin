---
name: hams-registry-collector
description: Claude Code 스킬/플러그인 레지스트리 수집 (큐레이션 소스)
---

# Registry Collector

GitHub의 큐레이션 소스와 MCP 레지스트리에서 Claude Code 스킬/플러그인을 수집하여 `~/.hamstern/skills-registry.json`을 생성합니다.

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

| 소스 | 규모 | 설명 |
|------|------|------|
| `hesreallyhim/awesome-claude-code` | ~190개 | 큐레이션된 스킬/에이전트/플러그인 |
| `glama.ai` | ~10개 | 인기 MCP 서버 (상위 30개 중 우선순위) |

## 수집된 데이터 예

```bash
/hams-registry-collector

🔄 Collecting skill registry from curated sources...

📚 awesome-claude-code 수집...
   ✓ Added 190 awesome skills
🤖 glama.ai MCP 서버 수집...
   ✓ Added 10 MCP servers

✅ Registry updated: ~/.hamstern/skills-registry.json

📊 Total skills: 197
   ├─ awesome: 187
   ├─ mcp: 10
   └─ avg popularity: 0.59 (max: 0.6)
```

## 출력 형식

```json
[
  {
    "id": "awesome:test-driven-development",
    "provider": "awesome",
    "name": "Test-Driven Development",
    "description": "TDD 워크플로우: 테스트 먼저 작성, 구현, 검증",
    "category": "engineering-workflow",
    "icon": "🧪",
    "github_repo": "anthropics/claude-code",
    "github_stars": 5420,
    "popularity_score": 0.85
  },
  {
    "id": "mcp:sequential-thinking",
    "provider": "mcp",
    "name": "Sequential Thinking",
    "description": "Step-by-step reasoning MCP server",
    "category": "integration",
    "icon": "🔗",
    "github_repo": "anthropics/mcp-servers",
    "github_stars": 2000,
    "popularity_score": 0.75
  },
  ...
]
```

## 메타데이터 필드

- `id` — 스킬 식별자 (provider:name)
- `provider` — 제공자 (awesome, mcp, registry 등)
- `name` — 스킬/플러그인 이름
- `description` — 한 줄 설명
- `category` — 카테고리 (engineering-workflow, testing, debugging, deployment 등)
- `icon` — 이모지
- `github_repo` — GitHub 저장소 (owner/repo)
- `github_stars` — GitHub 스타 수 (0일 수 있음)
- `popularity_score` — 인기도 점수 (0.0~1.0)

## 증분 업데이트

매번 호출할 때마다:
1. 각 소스에서 최신 데이터 수집
2. 기존 registry와 병합
3. id 기준으로 중복 제거 (새 데이터가 우선)
4. 결과를 registry.json에 저장

```
첫 실행:     197개 수집 → registry.json에 저장
두 번째 실행: 200개 수집 + 197개 기존 → 중복 제거 → 200개 저장
```

## 저장 위치

```
~/.hamstern/skills-registry.json
```

## 사용 사례

### 1. 수동 업데이트

```bash
/hams-registry-collector

# 현재 프로젝트의 스킬과 비교하려면 /hams-skill-picker 실행
/hams-skill-picker
```

### 2. 자동화 (선택)

`/schedule` 스킬로 정기 업데이트 스케줄링 (예: 주 1회):

```bash
/schedule "0 9 * * MON" /hams-registry-collector
```

### 3. /hams-skill-picker에서 활용

skill-picker가 registry를 읽어서:
- 설치된 스킬 vs 전체 스킬 비교
- 이 프로젝트에서 미사용 스킬 발견
- 인기도 기반 추천

## 기술 상세

### 데이터 소스

**awesome-claude-code (hesreallyhim)**
- README.md raw 다운로드 (API 호출 없음)
- 마크다운 링크 파싱: `- [name](url) - description`
- GitHub 레포 URL 추출

**glama.ai MCP Servers**
- REST API: `https://glama.ai/api/mcp/v1/servers?sort=popularity&limit=30`
- 인증 없음
- 인기순으로 상위 30개 반환

### 성능

- awesome 수집: ~2초 (raw.githubusercontent.com raw 다운로드)
- MCP 수집: ~1초 (glama.ai API 호출)
- 병합 및 저장: <1초
- **총 소요시간**: ~3초

### 캐싱

캐싱 없음. 매번 최신 데이터 수집.

---

## 주의사항

- 인터넷 연결 필수
- awesome-claude-code URL이 변경될 경우 스크립트 업데이트 필요
- glama.ai API 서버 다운 시 MCP 수집 실패 가능

---

## 팁

- `/hams-skill-picker`와 함께 사용하면 프로젝트에 필요한 스킬을 빠르게 찾을 수 있음
- registry.json은 버전 관리 대상 아님 (자동 생성)
- GITHUB_TOKEN 환경변수는 현재 사용 안 됨 (API 호출 최소화)
