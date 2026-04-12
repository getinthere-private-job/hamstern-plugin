---
name: hams-skill-picker
description: 현재 상황에서 최적의 스킬 추천 (프로젝트 맥락 기반)
dispatch: subagent
subagent_type: general-purpose
model: haiku
---

# Skill Picker

당신이 "지금 이 상황에는 어떤 스킬을 쓸까?"라고 물을 때, 
프로젝트 맥락을 보고 최적의 스킬을 추천해줍니다.

## 어떻게 작동하나?

1. **decisions.md 읽기** (있으면)
   - 이 프로젝트의 확정된 방향 파악

2. **hamstern-nagging.md 읽기** (있으면)
   - 이 프로젝트에서 자주 쓰는 스킬들

3. **skills-registry.json 읽기** (있으면)
   - 세상의 인기 스킬들과 메타데이터

4. **Haiku 분석**
   - 위 3개의 맥락을 종합해서
   - 지금 상황에 최적의 스킬 3-5개 추천

## 사용 예시

```bash
# 상황을 설명하고 스킬을 물어봐
# 예: "버그를 찾고 있는데, 어떤 스킬을 쓸까?"
# 예: "새 기능 개발 시작하는데 뭐부터?"
# 예: "코드 리뷰해야 하는데 어떻게?"

hams-skill-picker --context "현재 상황 설명"
```

## 추천 결과

```
🎯 추천 순서대로:

1. /gstack:investigate
   이유: 버그를 찾기 위해 체계적인 디버깅이 필요해 보임
   이 프로젝트에서: 사용률 75% (4회 사용)

2. /superpowers:test-driven-development
   이유: 버그 원인을 테스트로 검증하면 좋음
   이 프로젝트에서: 사용률 82% (5회 사용)

3. /gstack:review
   이유: 버그 수정 후 리뷰 받기
   이 프로젝트에서: 사용률 60% (3회 사용)

---

[1번: /gstack:investigate 지금 시작하기]
```

## 맥락 파일 (선택사항, 없어도 작동)

**필요한 파일들:**
- `~/.hamstern/hamstern-nagging.md` (프로젝트별 스킬 통계)
- `~/.hamstern/skills-registry.json` (세계 스킬 메타데이터)
- `{project_root}/.hamstern/boss-hamster/decisions.md` (프로젝트 방향)

파일이 없어도 Haiku가 기본 분석으로 추천합니다.

---

**Tip:** "이런 상황에는 뭘 쓸까?" 하고 생각날 때마다 `/hams-skill-picker`를 쓰세요!
