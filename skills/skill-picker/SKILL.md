---
name: hams-skill-picker
description: 현재 상황에서 최적의 스킬 추천 (프로젝트 맥락 기반)
dispatch: subagent
subagent_type: general-purpose
model: opus
---

# Skill Picker

당신이 "지금 이 상황에는 어떤 스킬을 쓸까?"라고 물을 때,
프로젝트 맥락을 보고 최적의 스킬을 추천하고 설치 방법까지 알려줍니다.

## 어떻게 작동하나?

1. **설치된 플러그인 확인**
   - `~/.claude/settings.json` 읽기
   - `enabledPlugins` 에서 `true` 인 항목 추출 → 설치된 플러그인 목록

2. **decisions.md 읽기** (있으면)
   - `{project_root}/.hamstern/boss-hamster/decisions.md`
   - 이 프로젝트의 확정된 방향 파악

3. **skills-registry.json 읽기** (있으면)
   - `~/.hamstern/skills-registry.json`
   - 세상의 인기 스킬들과 메타데이터

4. **분석 및 추천**
   - 유사 스킬 그룹핑 → 설치된 스킬 우선
   - 최적의 스킬 3-5개 추천 + 설치 여부 표시

## 설치 여부 확인 방법

`enabledPlugins` 키 형식: `{plugin-name}@{marketplace-name}`

추천 스킬의 플러그인 이름(`:` 앞부분)이 `enabledPlugins`에 `true`로 있으면 설치됨.

예: `/gstack:investigate` → `gstack` → `gstack@{marketplace}` 가 `true` 이면 ✅

## 유사 스킬 우선순위 규칙

같은 목적의 스킬이 여러 개일 때:

1. **✅ 설치된 스킬 먼저** — 미설치보다 항상 우선
2. **유사한 것들은 그룹으로 묶기** — 개별 나열 금지
3. **비교 설명 포함** — "A는 설치됨, B는 더 강력하지만 설치 필요"

## 추천 결과 형식

```
🎯 추천 순서대로:

1. ✅ /superpowers:systematic-debugging  [설치됨]
   이유: 체계적인 디버깅 워크플로우 — 바로 사용 가능
   유사 스킬: ⚠️ /gstack:investigate (더 강력하나 설치 필요)
              설치: /plugin marketplace add garrytan/gstack
                    /plugin install gstack

2. ✅ /superpowers:test-driven-development  [설치됨]
   이유: 버그 원인을 테스트로 검증

3. ⚠️  /everything-claude-code:research  [미설치]
   이유: 위 스킬로 해결 안 될 때 — 광범위한 에이전트
   설치: /plugin marketplace add affaan-m/everything-claude-code
         /plugin install everything-claude-code
```

## 설치 커맨드 생성 규칙

- registry에 `github_repo` 있으면: `/plugin marketplace add {github_repo}` + `/plugin install {name}`
- `claude-plugins-official` 마켓플레이스 플러그인이면: `/plugin install {name}@claude-plugins-official`
- 정보 없으면: `/plugin marketplace add {github_repo}` 만 안내

## 맥락 파일 (선택사항, 없어도 작동)

- `~/.claude/settings.json` — 설치된 플러그인 확인 (필수)
- `~/.hamstern/skills-registry.json` — 스킬 메타데이터
- `{project_root}/.hamstern/boss-hamster/decisions.md` — 프로젝트 방향

---

**Tip:** "이런 상황에는 뭘 쓸까?" 하고 생각날 때마다 `/hams-skill-picker`를 쓰세요!
