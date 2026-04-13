# hams-context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/hams-context` 슬래시 커맨드로 `boss-hamster/decisions.md` 를 현재 세션에 로드하는 스킬을 만든다.

**Architecture:** `skills/context/SKILL.md` 파일 하나를 만들고, `marketplace.json` 에 등록한다. 스킬 실행 시 Claude가 decisions.md 를 Read 툴로 읽어 컨텍스트에 주입하고 확인 메시지를 출력한다.

**Tech Stack:** Markdown (SKILL.md), JSON (marketplace.json)

---

### Task 1: SKILL.md 생성

**Files:**
- Create: `skills/context/SKILL.md`

- [ ] **Step 1: `skills/context/SKILL.md` 파일 생성**

```markdown
---
name: hams-context
description: boss-hamster/decisions.md 를 현재 세션에 로드 (결정사항 재주입)
allowed-tools:
  - Read
---

# /hams-context

현재 프로젝트의 확정된 결정사항을 세션에 로드합니다.
`/clear` 이후나 새 세션 시작 시 수동으로 실행하세요.

## 동작

1. `{project_root}/.hamstern/boss-hamster/decisions.md` 를 Read 툴로 읽는다
2. 내용을 그대로 컨텍스트에 로드한다
3. 아래 형식으로 확인 출력한다:

```
📌 decisions.md 로드됨 ({n}개 결정사항)
이 세션에서는 위 결정사항들을 따릅니다.
```

## 결정사항 개수 세기

decisions.md 에서 `##` 또는 `- ` 로 시작하는 항목 수를 세어 `{n}` 에 대입한다.
정확하지 않아도 됨 — 대략적인 숫자면 충분.

## project_root 찾기

현재 작업 디렉토리 또는 git root 기준으로
`.hamstern/boss-hamster/decisions.md` 파일을 찾는다.
```

- [ ] **Step 2: 커밋**

```bash
git add skills/context/SKILL.md
git commit -m "feat: hams-context 스킬 추가"
```

---

### Task 2: marketplace.json 등록

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: `plugins[0].skills` 배열에 `./skills/context` 추가**

현재 파일:
```json
{
  "plugins": [
    {
      "skills": [
        "./skills/skill-picker",
        "./skills/dashboard",
        "./skills/audit-decisions",
        "./skills/registry-collector"
      ]
    }
  ]
}
```

수정 후:
```json
{
  "plugins": [
    {
      "skills": [
        "./skills/skill-picker",
        "./skills/dashboard",
        "./skills/audit-decisions",
        "./skills/registry-collector",
        "./skills/context"
      ]
    }
  ]
}
```

- [ ] **Step 2: 커밋**

```bash
git add .claude-plugin/marketplace.json
git commit -m "chore: hams-context 스킬 marketplace 등록"
```

---

### Task 3: 수동 검증

**Files:** 없음 (확인만)

- [ ] **Step 1: 테스트용 decisions.md 확인**

테스트할 프로젝트의 `.hamstern/boss-hamster/decisions.md` 가 존재하는지 확인.
없으면 임시로 아래 내용으로 생성:

```markdown
## architecture
- baby/mom/boss 3폴더 구조 확정

## performance
- 3-turn 요약 시스템 제거
```

- [ ] **Step 2: `/hams-context` 실행 후 출력 확인**

기대 출력:
```
📌 decisions.md 로드됨 (2개 결정사항)
이 세션에서는 위 결정사항들을 따릅니다.
```

그리고 decisions.md 내용이 Claude 응답 위에 표시되는지 확인.
