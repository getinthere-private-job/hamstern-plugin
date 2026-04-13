# hamstern 플러그인 재설계 스펙

**날짜:** 2026-04-14
**대상:** `skills/dashboard/`, `skills/context/`, `.claude/settings.json`

---

## 1. 배경 및 목표

### 핵심 문제

1. Claude compact 후 프로젝트 결정사항이 사라짐 — 개발자가 Claude가 무엇을 알고 있는지 볼 수 없음
2. 여러 Claude 인스턴스가 동시에 작업 시 각자의 지식이 통합되지 않음

### 설계 원칙

- **"보이는 것 = 실제 주입되는 것"** — 대시보드가 보여주는 내용과 CLAUDE.md에 주입되는 내용이 동일한 소스(`decisions.md`)에서 나온다
- **앱 없이도 동작, 앱 있으면 더 강력** — 플러그인 단독으로 완전한 워크플로우 제공
- **사람이 최종 결정** — 자동화는 후보 추출까지, 확정은 핀으로

### 변경사항 요약

- `hams-audit-decisions` 스킬 **제거** (대시보드에 통합)
- `hams-compact` 스킬 **제거** (불필요)
- `hams-dashboard` **재설계** (3컬럼 UI + Opus 추론 + 2단계 핀)
- `hams-context` **재설계** (훅 자동 주입 추가)
- 훅 시스템 **신규 추가** (baby MD 폴백 기록 + CLAUDE.md 자동 주입)

---

## 2. 시스템 개요

```
┌─────────────────────────────────────────────────────────────┐
│                      hamstern 생태계                         │
│                                                             │
│  ┌─────────────────────┐    ┌──────────────────────────┐   │
│  │   hamstern 앱        │    │   hamstern 플러그인       │   │
│  │  (Swift, cmux 포크)  │    │  (Claude Code 스킬+훅)   │   │
│  │                     │    │                          │   │
│  │ - 터미널 I/O 캡처     │    │ - baby MD 폴백 기록       │   │
│  │ - baby MD 기록       │◄───┤ - decisions → CLAUDE.md  │   │
│  │ - ML 핀 추천         │    │ - hams-dashboard         │   │
│  │ - 탭 배지/사이드바    │    │ - hams-context           │   │
│  └─────────────────────┘    └──────────────────────────┘   │
│              │                          │                   │
│              └──────────┬───────────────┘                   │
│                         ▼                                   │
│              ┌──────────────────────┐                       │
│              │  .hamstern/ (공유 저장소) │                   │
│              └──────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 역할 분담

### 3.1 hamstern 앱 (실행 중일 때)

| 역할 | 상세 |
|------|------|
| baby MD 기록 | 터미널 I/O 직접 캡처 → `surface_{uuid}.md` |
| mom MD 집계 | 모든 baby MD 읽어 `mom.md` 생성/갱신 |
| ML 핀 추천 | 중요 결정사항 후보 자동 감지 |
| 네이티브 UI | 탭 배지, Agent/Skill 사이드바 |
| 앱 실행 신호 | `.hamstern/.app-running` 생성/삭제 |

### 3.2 hamstern 플러그인 (항상)

| 역할 | 조건 | 상세 |
|------|------|------|
| baby MD 폴백 기록 | 앱 없을 때만 | `UserPromptSubmit` + `Stop` 훅 |
| mom MD 집계 트리거 | 앱 없을 때만 | `SessionEnd` 훅 → 스크립트 |
| decisions → CLAUDE.md | 항상 | `/hams-context` + `SessionStart` 훅 |
| Opus 추론 + 핀 UI | 항상 | `/hams-dashboard` |

### 3.3 앱 감지

`.hamstern/.app-running` 파일 존재로 판단. mtime이 24시간 초과면 stale로 간주하고 플러그인이 인수.

```bash
APP_RUNNING=".hamstern/.app-running"
if [ -f "$APP_RUNNING" ]; then
  AGE=$(( $(date +%s) - $(stat -c %Y "$APP_RUNNING" 2>/dev/null || echo 0) ))
  [ $AGE -gt 86400 ] && rm "$APP_RUNNING"  # stale 제거
fi
```

---

## 4. 데이터 플로우

### 4.1 앱 + 플러그인 동시 실행

```
[터미널 I/O]
     │ hamstern 앱
     ▼
surface_{uuid}.md ──────────────────────────┐
                                            │
[Claude Code 훅] SessionStart               ▼
     │ .app-running 존재 확인        .hamstern/baby-hamster/
     │ → CLAUDE.md 주입만                   │
     │ → baby 훅 비활성화             hams-dashboard 실행
                                            │
                                    Opus 추론 + 2단계 핀
                                            │
                              ┌─────────────┴──────────────┐
                              ▼                            ▼
                       decisions.md              decisions-log.md
                              │
                              ▼
                          CLAUDE.md (마커 교체)
```

### 4.2 플러그인 단독 실행

```
[UserPromptSubmit 훅]      [Stop 훅]
        │                      │
        ▼                      ▼
session_{session_id}.md (대화 순차 기록)
        │
[SessionEnd 훅]
        │
        ▼
mom MD 집계 스크립트 (Python, 단순 병합)
        │
        ▼
hams-dashboard → Opus 추론 → 핀 → decisions.md → CLAUDE.md
```

### 4.3 compact 보호

```
SessionStart(source=compact) 훅
     ↓
decisions.md → CLAUDE.md 마커 교체
     ↓
Claude가 최신 결정사항을 갖고 새 컨텍스트 시작
```

---

## 5. 파일 구조

```
{프로젝트 루트}/
├── CLAUDE.md                           # decisions 주입 대상
└── .hamstern/
    ├── .app-running                    # 앱 실행 신호 (앱이 관리)
    ├── baby-hamster/
    │   ├── session_{session_id}.md     # 플러그인 기록 (훅 기반)
    │   └── surface_{uuid}.md          # 앱 기록 (터미널 I/O)
    ├── mom-hamster/
    │   └── mom.md                     # baby MD 집계본
    └── boss-hamster/
        ├── decisions.md               # 현재 활성 결정사항 (단일 진실)
        └── decisions-log.md           # append-only 이력
```

**파일 소유권:**

| 파일 | 생성 | 갱신 | 수명 |
|------|------|------|------|
| `.app-running` | 앱 | 앱 | 앱 실행 중만 |
| `session_{id}.md` | 플러그인 Stop 훅 | 불변 | 영구 |
| `surface_{uuid}.md` | 앱 | 불변 | 영구 |
| `mom.md` | 대시보드/스크립트 | Opus | 집계 시 전체 갱신 |
| `decisions.md` | 대시보드 | 핀 확정 시 | 핀 변경마다 |
| `decisions-log.md` | 대시보드 | append-only | 영구 누적 |
| `CLAUDE.md` | 사용자/플러그인 | 마커 블록만 자동 | decisions 변경 시 |

---

## 6. hams-dashboard 스킬

### 6.1 실행 플로우

```
/hams-dashboard [--port 7777]
  ↓
포트 충돌 확인 (lsof -ti:7777)
  ↓
skills/dashboard/server.py 백그라운드 실행
  ↓
초기 데이터 로드 (baby MDs + mom.md)
  ↓
브라우저 오픈 (http://localhost:7777)
  ↓
Opus 비동기 분석 시작 (백그라운드)
```

Claude 출력:
```
🚀 hams-dashboard 시작 중...
   포트: 7777
   데이터: .hamstern/ (baby 3개, mom.md 존재)
   Opus 분석: 백그라운드 실행 중...

브라우저가 열립니다: http://localhost:7777
분석 완료 시 대시보드가 자동 업데이트됩니다.
```

### 6.2 서버 아키텍처

```
skills/dashboard/
├── SKILL.md
├── server.py          # Python HTTP 서버 (stdlib only)
├── static/
│   └── index.html     # 전체 UI (단일 파일, vanilla JS)
└── scripts/
    └── aggregate.py   # baby MD → mom MD 집계 (앱 없을 때)
```

서버는 `python3 -m` 없이 stdlib만 사용 (`http.server`, `json`, `subprocess`).

### 6.3 API 명세

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/` | 대시보드 HTML |
| `GET` | `/api/baby` | baby MD 목록 + 내용 |
| `GET` | `/api/mom` | mom.md 내용 |
| `GET` | `/api/decisions` | decisions.md 내용 |
| `POST` | `/api/analyze` | Opus 재분석 트리거 |
| `GET` | `/api/analyze/status` | 분석 진행 상태 폴링 |
| `POST` | `/api/pin/mom` | mom-level 핀 토글 |
| `POST` | `/api/pin/boss` | boss-level 핀 → decisions.md |
| `DELETE` | `/api/pin/boss/{id}` | 결정사항 제거 |

**POST /api/analyze 요청:**
```json
{ "mom_pins": ["핀된 항목 1", "핀된 항목 2"] }
```

**POST /api/pin/boss 요청:**
```json
{
  "decision": "baby/mom/boss 3폴더 구조 확정",
  "category": "Architecture",
  "background": "Opus 추론 요약",
  "source_session": "abc-123"
}
```

### 6.4 UI 레이아웃

```
┌──────────────────────────────────────────────────────────────────────┐
│  🐹 hams-dashboard                              [재분석] [설정]       │
├──────────────┬───────────────────────────────┬──────────────────────┤
│  Baby MDs    │  Mom MD + Audit               │  decisions.md        │
│  (200px)     │  (flex-grow)                  │  (280px)             │
│              │                               │                      │
│ 📄 session1  │  ## 개요                      │  ## Architecture     │
│ 📄 session2  │  ...mom.md 내용...            │  - 3폴더 구조 확정    │
│ 📄 session3  │                               │                      │
│ 📄 surface1  │  ─────────────────────────    │  ## Performance      │
│              │  🔍 Opus 추론 결과             │  - JSONL 제거        │
│  [앱 기록]    │                               │                      │
│  [훅 기록]   │  ┌─────────────────────────┐  │  ## UI               │
│              │  │ 📌 3컬럼 레이아웃 확정    │  │  - 3컬럼 레이아웃    │
│              │  │ Architecture             │  │                      │
│              │  │ "Audit 패널 독립 운용..."  │  │                      │
│              │  │ [mom 핀 📌] [확정 ✅]     │  │                      │
│              │  └─────────────────────────┘  │                      │
│              │  ┌─────────────────────────┐  │                      │
│              │  │ ⚠️ JSONL 제거           │  │                      │
│              │  │ Performance              │  │                      │
│              │  │ [mom 핀 📌] [확정 ✅]   │  │                      │
│              │  └─────────────────────────┘  │                      │
└──────────────┴───────────────────────────────┴──────────────────────┘
```

**카드 상태:**
- 기본: 흰 배경, 회색 테두리
- mom 핀됨: 노란 배경 (`#FFF9C4`)
- boss 확정됨: 초록 테두리 (`#4CAF50`)
- 충돌: 빨간 테두리 (`#F44336`)

### 6.5 Opus 추론 프로세스

**프롬프트 구조:**
```
다음은 프로젝트 대화 기록(mom MD)입니다.
중복을 제거하고 명확한 결정사항만 추출하세요.

[mom MD 핀된 항목 - 우선 처리]
{mom_pins}

[전체 mom MD]
{mom_content}

출력 형식:
카테고리별로 결정사항을 JSON 배열로 반환하세요.
각 항목: { "decision", "category", "background", "confidence" }
```

**중복 제거:** Jaccard 유사도 70% 이상이면 동일 결정으로 판단, 최신 것 유지.

**상태 폴링:** `/api/analyze/status` → `{ "status": "running|done", "progress": 0.7, "results": [...] }`

### 6.6 2단계 핀 플로우

**mom-level 핀** (중요하지만 미결):
```
[mom 핀 📌] 클릭
  → POST /api/pin/mom { "item": "...", "pinned": true }
  → 카드에 노란 배경 표시
  → 다음 [재분석] 시 Opus 프롬프트에 가중치 부여
```

**boss-level 핀** (최종 확정):
```
[확정 ✅] 클릭
  → POST /api/pin/boss { decision, category, background, source }
  → decisions.md 재생성
  → decisions-log.md append
  → CLAUDE.md 마커 섹션 자동 업데이트
  → 오른쪽 패널 즉시 반영
```

**충돌 카드:**
```
┌─────────────────────────────────────────────────┐
│ ⚠️ 결정 충돌 감지                                │
│ 기존: "2컬럼 레이아웃" (2026-04-10)              │
│ 새 제안: "3컬럼 레이아웃"                         │
│ [새 제안으로 교체] [기존 유지] [둘 다 보류]        │
└─────────────────────────────────────────────────┘
```

---

## 7. 훅 시스템

### 7.1 SessionStart 훅 (CLAUDE.md 자동 주입)

compact 또는 새 세션 시작 시 decisions.md → CLAUDE.md 자동 주입.

```bash
#!/bin/bash
# ~/.claude/hooks/session-start.sh

DECISIONS=".hamstern/boss-hamster/decisions.md"
CLAUDE_MD="CLAUDE.md"
START_MARKER="<!-- hamstern:decisions:start -->"
END_MARKER="<!-- hamstern:decisions:end -->"

[ ! -f "$DECISIONS" ] && exit 0  # decisions.md 없으면 조용히 종료

CONTENT=$(cat "$DECISIONS")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S")

BLOCK="${START_MARKER}
## 현재 프로젝트 결정사항 (hamstern 자동 주입)

_업데이트: ${TIMESTAMP}_

${CONTENT}
${END_MARKER}"

if grep -q "$START_MARKER" "$CLAUDE_MD" 2>/dev/null; then
  # 기존 마커 블록 교체
  python3 -c "
import re, sys
content = open('$CLAUDE_MD').read()
block = '''$BLOCK'''
result = re.sub(r'<!-- hamstern:decisions:start -->.*?<!-- hamstern:decisions:end -->', block, content, flags=re.DOTALL)
open('$CLAUDE_MD', 'w').write(result)
"
else
  # 마커 없으면 파일 끝에 추가
  echo "" >> "$CLAUDE_MD"
  echo "$BLOCK" >> "$CLAUDE_MD"
fi
```

### 7.2 baby MD 폴백 기록

앱 없을 때만 동작.

**UserPromptSubmit 훅:**
```bash
#!/bin/bash
# ~/.claude/hooks/user-prompt.sh

APP_RUNNING=".hamstern/.app-running"
[ -f "$APP_RUNNING" ] && exit 0  # 앱 있으면 양보

SESSION_ID=$(echo "$CLAUDE_HOOK_DATA" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['session_id'])")
PROMPT=$(echo "$CLAUDE_HOOK_DATA" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('prompt',''))")

BABY_DIR=".hamstern/baby-hamster"
mkdir -p "$BABY_DIR"
BABY_FILE="$BABY_DIR/session_${SESSION_ID}.md"

# 헤더 (최초 1회)
if [ ! -f "$BABY_FILE" ]; then
  cat > "$BABY_FILE" << EOF
---
session_id: ${SESSION_ID}
started_at: $(date -u +"%Y-%m-%dT%H:%M:%S")
cwd: $(pwd)
source: plugin-hook
---
EOF
fi

# 턴 카운트
TURN=$(grep -c "^## Turn" "$BABY_FILE" 2>/dev/null || echo 0)
TURN=$((TURN + 1))
echo "" >> "$BABY_FILE"
echo "## Turn ${TURN}" >> "$BABY_FILE"
echo "**User:** ${PROMPT}" >> "$BABY_FILE"
```

**Stop 훅:**
```bash
#!/bin/bash
# ~/.claude/hooks/stop.sh

APP_RUNNING=".hamstern/.app-running"
[ -f "$APP_RUNNING" ] && exit 0

SESSION_ID=$(echo "$CLAUDE_HOOK_DATA" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['session_id'])")
TRANSCRIPT=$(echo "$CLAUDE_HOOK_DATA" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('transcript_path',''))")

BABY_FILE=".hamstern/baby-hamster/session_${SESSION_ID}.md"
[ ! -f "$BABY_FILE" ] && exit 0

# transcript에서 마지막 assistant 메시지 추출
if [ -f "$TRANSCRIPT" ]; then
  LAST_MSG=$(python3 -c "
import json
msgs = [json.loads(l) for l in open('$TRANSCRIPT') if l.strip()]
assistant = [m for m in msgs if m.get('role') == 'assistant']
print(assistant[-1]['content'] if assistant else '')
" 2>/dev/null)
  echo "**Claude:** ${LAST_MSG}" >> "$BABY_FILE"
fi
```

### 7.3 mom MD 집계 (플러그인 단독 모드)

SessionEnd 훅 또는 hams-dashboard 시작 시 실행.

```python
# scripts/aggregate.py
import os, re
from pathlib import Path

def aggregate_baby_to_mom(project_root):
    baby_dir = Path(project_root) / ".hamstern" / "baby-hamster"
    mom_file = Path(project_root) / ".hamstern" / "mom-hamster" / "mom.md"
    mom_file.parent.mkdir(exist_ok=True)

    babies = sorted(baby_dir.glob("*.md"), key=lambda f: f.stat().st_mtime)
    seen_sessions = set()
    combined = []

    for baby in babies:
        content = baby.read_text()
        # session_id 중복 체크
        m = re.search(r'session_id:\s*(\S+)', content)
        sid = m.group(1) if m else baby.stem
        if sid in seen_sessions:
            continue
        seen_sessions.add(sid)
        combined.append(f"<!-- source: {baby.name} -->\n{content}")

    mom_file.write_text("\n\n---\n\n".join(combined))
```

### 7.4 settings.json 설정

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/session-start.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/user-prompt.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/stop.sh"
          }
        ]
      }
    ]
  }
}
```

---

## 8. decisions 파이프라인

### 8.1 decisions.md 포맷

```markdown
# 프로젝트 결정사항

_마지막 업데이트: 2026-04-14T15:30:00_
_업데이트 방법: /hams-dashboard에서 핀으로 확정_

## Architecture
- baby/mom/boss 3폴더 구조 확정

## Performance
- JSONL 완전 제거

## UI
- 대시보드 3컬럼 레이아웃
```

**규칙:** 사람이 직접 편집 안 함. hams-dashboard가 핀 확정 시 전체 재생성.

### 8.2 decisions-log.md 포맷 (append-only)

```markdown
# Decisions Log
<!-- append-only. 수동 편집 금지. -->

---

## 2026-04-14T15:30:00 | 핀 추가
- **결정:** baby/mom/boss 3폴더 구조 확정
- **카테고리:** Architecture
- **배경:** 성격별로 분리해야 Opus 추론 정확도가 높아짐
- **출처:** mom MD · session abc-123

---

## 2026-04-14T15:31:00 | 핀 제거
- **결정:** HTTP 대시보드 JSONL 방식
- **카테고리:** Performance
- **제거 이유:** 사용자가 제외 선택
```

### 8.3 CLAUDE.md 마커 주입

```markdown
<!-- hamstern:decisions:start -->
## 현재 프로젝트 결정사항 (hamstern 자동 주입)

_업데이트: 2026-04-14T15:30:00_

### Architecture
- baby/mom/boss 3폴더 구조 확정

### Performance
- JSONL 완전 제거
<!-- hamstern:decisions:end -->
```

**교체 알고리즘:**
1. CLAUDE.md에서 마커 검색
2. 마커 없으면 파일 끝에 append
3. 마커 있으면 start~end 사이만 교체
4. 마커 밖 내용 보존

### 8.4 hams-context 스킬 재설계

수동 실행 시:
```
📌 decisions.md 로드됨 (12개 결정사항)
CLAUDE.md 마커 섹션 업데이트 완료.
이 세션에서는 위 결정사항들을 따릅니다.
```

decisions.md 없을 때:
```
decisions.md 없음.
/hams-dashboard를 먼저 실행해 결정사항을 확정하세요.
```

훅으로 자동 실행 시: 조용히 종료 (에러 없이).

---

## 9. 앱+플러그인 시너지

| 구간 | 앱 | 플러그인 |
|------|-----|---------|
| baby MD 기록 | 터미널 I/O 전체 (세밀) | 훅 이벤트만 (폴백) |
| mom MD 집계 | 자동 (상시) | SessionEnd 트리거 |
| Opus 추론 | - | hams-dashboard |
| 핀 UI | - | hams-dashboard |
| decisions.md 쓰기 | - | hams-dashboard API |
| CLAUDE.md 주입 | - | SessionStart 훅 + /hams-context |
| ML 핀 추천 | 네이티브 (on-device) | - |
| 탭 배지/사이드바 | 네이티브 GUI | - |

**앱이 없어도:** 전체 decisions 워크플로우 동작, baby MD 훅 기록, CLAUDE.md 자동 주입
**앱이 있으면:** 더 세밀한 baby MD, ML 추천, 네이티브 UI, 더 빠른 mom MD 집계
