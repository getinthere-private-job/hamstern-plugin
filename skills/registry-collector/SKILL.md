---
name: registry-collector
description: 전역 스킬 레지스트리 수집 (GitHub, MCP)
---

# Registry Collector

GitHub과 MCP에서 스킬들을 수집하여 `~/.hamstern/skills-registry.json`을 생성합니다.

이 데이터는 `/hams:skill-picker`에서 스킬 추천 시 참고됩니다.

## 동작

```bash
/hams:registry-collector [--force]
```

**옵션:**
- `--force` — 캐시 무시하고 즉시 수집 (기본: 24시간 캐시)

## 수집 대상

### 1. GitHub: superpowers 스킬
```
https://github.com/anthropics/claude-code
└─ superpowers/*
   ├─ superpowers:test-driven-development
   ├─ superpowers:systematic-debugging
   ├─ superpowers:writing-plans
   └─ ... (모든 superpowers 스킬)
```

**메트릭:** Stars, Forks, Last Updated

### 2. GitHub: gstack 공개 스킬
```
https://github.com/getinthere/gstack
└─ skills/*
   ├─ gstack:investigate
   ├─ gstack:ship
   ├─ gstack:design-review
   └─ ... (모든 gstack 스킬)
```

### 3. MCP: Anthropic 공식
```
https://github.com/anthropics/mcp
├─ filesystem
├─ postgres
├─ slack
└─ ... (모든 Anthropic MCP)
```

### 4. MCP: 커뮤니티
```
https://github.com/topics/mcp-server
└─ (인기 순서, top 50)
   ├─ community:langchain
   ├─ community:stripe
   └─ ...
```

## 출력 형식

```json
[
  {
    "id": "superpowers:test-driven-development",
    "provider": "superpowers",
    "name": "Test-Driven Development",
    "description": "TDD 워크플로우: 테스트 먼저 작성, 구현, 검증",
    "category": "engineering-workflow",
    "icon": "🧪",
    "github_repo": "anthropics/claude-code",
    "github_stars": 5420,
    "github_forks": 312,
    "github_last_updated": "2026-04-10T15:30:00Z",
    "installed": true,
    "installed_path": "~/.claude/skills/superpowers/test-driven-development",
    "popularity_score": 0.92
  },
  {
    "id": "gstack:ship",
    "provider": "gstack",
    "name": "Ship Workflow",
    "description": "배포 워크플로우: 머지, 빌드, 테스트, 배포",
    "category": "deployment",
    "icon": "🚀",
    "github_repo": "getinthere/gstack",
    "github_stars": 890,
    "github_forks": 45,
    "github_last_updated": "2026-04-08T10:00:00Z",
    "installed": false,
    "installed_path": null,
    "popularity_score": 0.78
  },
  ...
]
```

## 메타데이터

**파일 위치:**
```
~/.hamstern/skills-registry.json
```

**구조:**
- `id` — 스킬 식별자 (provider:name)
- `provider` — 제공자 (superpowers, gstack, mcp, community)
- `name` — 스킬 이름
- `description` — 한 줄 설명
- `category` — 카테고리 (engineering-workflow, debugging, deployment 등)
- `icon` — 이모지
- `github_repo` — GitHub 저장소 (owner/repo)
- `github_stars` — GitHub 스타 수
- `github_forks` — GitHub 포크 수
- `github_last_updated` — 마지막 업데이트
- `installed` — 현재 설치 여부
- `installed_path` — 설치 경로
- `popularity_score` — 인기도 점수 (0.0-1.0)

## 인기도 점수 계산

```
popularity_score = 
  0.5 * normalize(github_stars) +
  0.3 * normalize(github_forks) +
  0.2 * recency_boost(last_updated)

recency_boost:
  - 24시간 이내: +0.1
  - 7일 이내: +0.05
  - 30일 이내: 0
  - 30일 이상: -0.05
```

## 사용 사례

### 1. 초기 설정

```bash
# ~/.hamstern/skills-registry.json 생성
/hams:registry-collector

# 결과
✅ Collected 120 skills
  ├─ superpowers: 18
  ├─ gstack: 25
  ├─ mcp: 42
  └─ community: 35

Saved to: ~/.hamstern/skills-registry.json
```

### 2. 정기 업데이트 (주 1회)

```bash
/hams:registry-collector --force

✅ Updated registry
  ├─ New: 3 skills
  ├─ Updated: 12 skills
  └─ Removed: 1 skill
```

### 3. /hams:skill-picker에서 활용

skill-picker가 registry를 읽어서:
- 설치된 스킬 vs 전체 스킬 비교
- 이 프로젝트에서 미사용 스킬 발견
- 인기도 기반 추천

## 기술 세부사항

### GitHub API

```bash
# superpowers 스킬 목록
curl -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/anthropics/claude-code/contents/skills

# 각 스킬 메타데이터
curl -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/anthropics/claude-code/commits?path=skills/test-driven-development
```

### MCP 수집

- Anthropic 공식 MCP: `https://github.com/anthropics/mcp` 패키지 목록
- 커뮤니티 MCP: `https://github.com/topics/mcp-server` (top 50, stars 순)

### 캐싱

- **기본 캐시 기간:** 24시간
- **캐시 위치:** `~/.hamstern/.registry-cache.json`
- **--force 플래그로 캐시 무시 가능**

---

## 주의사항

- GitHub API 레이트 제한: 60 요청/시간 (인증 없을 시)
- 대량 수집 시 시간 소요 (3-5분)
- 인터넷 연결 필수
- GitHub 토큰 설정 시 레이트 제한 완화 가능:
  ```bash
  export GITHUB_TOKEN=<your-token>
  ```

---

## 팁

- 주 1회 자동 업데이트 스케줄링 권장 (근 /schedule 스킬 사용)
- skills-registry.json은 버전 관리 대상 아님 (자동 생성)
- 커스텀 스킬 추가는 hamstern-nagging.md에 직접 편집
