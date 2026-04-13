# hams-dashboard 스킬 디자인

**날짜:** 2026-04-13  
**대상 파일:** `skills/dashboard/SKILL.md`

---

## 개요

`/hams-dashboard` 는 로컬 Python HTTP 서버를 띄우고 브라우저를 자동 오픈하여, mom MD 데이터를 Opus 추론으로 분석한 결정사항 후보를 카드 UI로 보여주는 웹 대시보드 스킬이다.

mom-level 핀 → boss-level 확정 2단계 핀 시스템을 통해 decisions.md를 점진적으로 구축한다.

---

## 5. hams-dashboard 스킬

### 5.1 실행 플로우

```
/hams-dashboard 실행
    ↓
1. 포트 7777 사용 중 확인
   └─ 사용 중이면: 기존 프로세스 kill 후 재시작
    ↓
2. Python HTTP 서버 백그라운드 실행
   └─ server.py → localhost:7777
    ↓
3. 초기 데이터 로드
   ├─ mom MD 파일 목록 수집
   │   └─ {project_root}/.hamstern/mom-hamster/*.md
   ├─ decisions.md 읽기
   │   └─ {project_root}/.hamstern/boss-hamster/decisions.md
   └─ pins.json 읽기 (mom-level 핀 상태)
       └─ {project_root}/.hamstern/boss-hamster/pins.json
    ↓
4. Opus 초기 분석 실행 (비동기)
   └─ mom MD 전체 → 결정사항 후보 추출
    ↓
5. 브라우저 자동 오픈
   └─ http://localhost:7777
    ↓
6. 서버 계속 실행 (foreground 유지)
   └─ Ctrl+C로 종료
```

**Claude 출력 (실행 시):**
```
대시보드 서버를 시작합니다...
✓ 서버 실행: http://localhost:7777
✓ 브라우저 오픈 중...
✓ Opus 초기 분석 시작 (백그라운드)

종료하려면 Ctrl+C
```

**파일 경로 기준:**
- `{project_root}` = 현재 Claude Code 워킹 디렉토리
- 서버는 `{project_root}/.hamstern/` 경로를 기준으로 파일 접근

---

### 5.2 서버 아키텍처

**Approach B: Claude가 Python 경량 서버를 직접 실행**

```
[브라우저]
    │  HTTP GET/POST
    ▼
[Python HTTP 서버 :7777]
    │
    ├── GET /          → dashboard.html (인라인 번들)
    ├── GET /api/mom   → mom MD 파일 파싱 결과
    ├── GET /api/decisions → decisions.md 파싱 결과
    ├── POST /api/analyze  → Opus 분석 트리거
    ├── POST /api/pin/mom  → pins.json 업데이트
    ├── POST /api/pin/boss → decisions.md 기록
    └── DELETE /api/pin/boss/{id} → decisions.md 항목 삭제
         │
         └── [파일 시스템]
               ├── .hamstern/mom-hamster/*.md    (읽기 전용)
               ├── .hamstern/boss-hamster/decisions.md  (읽기/쓰기)
               └── .hamstern/boss-hamster/pins.json     (읽기/쓰기)
```

**서버 구현 파일 구조:**
```
skills/dashboard/
├── SKILL.md          ← Claude가 실행하는 스킬 진입점
└── server/
    ├── server.py     ← Python HTTP 서버 (단일 파일)
    └── dashboard.html ← 브라우저 UI (인라인 CSS/JS 포함)
```

**server.py 핵심 구조:**
```python
import http.server
import json
import os
import subprocess
import threading
from pathlib import Path

PROJECT_ROOT = os.environ.get("HAMSTERN_PROJECT_ROOT", os.getcwd())
PORT = int(os.environ.get("HAMSTERN_PORT", 7777))
HAMSTERN_DIR = Path(PROJECT_ROOT) / ".hamstern"
MOM_DIR = HAMSTERN_DIR / "mom-hamster"
BOSS_DIR = HAMSTERN_DIR / "boss-hamster"
DECISIONS_FILE = BOSS_DIR / "decisions.md"
PINS_FILE = BOSS_DIR / "pins.json"

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self): ...
    def do_POST(self): ...
    def do_DELETE(self): ...
```

**Claude가 서버 실행하는 방법 (SKILL.md에서):**
```bash
export HAMSTERN_PROJECT_ROOT=$(pwd)
export HAMSTERN_PORT=7777
python3 skills/dashboard/server/server.py &
```
서버 PID를 기록했다가 스킬 종료 시 kill.

**서버 시작 전 포트 충돌 처리:**
```bash
# 7777 포트 사용 중인 프로세스 확인 후 kill
lsof -ti:7777 | xargs kill -9 2>/dev/null || true
```

---

### 5.3 API 명세

#### GET /
대시보드 HTML 반환.

```
Response: text/html; charset=utf-8
Body: dashboard.html 전체 내용
```

---

#### GET /api/mom

mom MD 파일 목록과 각 파일의 메타데이터 반환.

```json
Response 200:
{
  "sessions": [
    {
      "id": "2026-04-13-session-01",
      "filename": "2026-04-13-session-01.md",
      "date": "2026-04-13",
      "title": "세션 제목 (첫 번째 H1 또는 파일명)",
      "preview": "첫 200자 미리보기",
      "size_bytes": 3421,
      "pinned_count": 2
    }
  ],
  "total": 5
}
```

---

#### GET /api/decisions

decisions.md 현재 내용과 파싱된 항목 목록 반환.

```json
Response 200:
{
  "raw": "# 결정사항\n\n...",
  "items": [
    {
      "id": "dec-uuid-1234",
      "content": "결정사항 한 줄 요약",
      "context": "결정 배경 및 근거",
      "date_added": "2026-04-13",
      "source": "boss-level-pin"
    }
  ],
  "count": 3
}
```

---

#### POST /api/analyze

Opus 재분석 트리거. mom MD 전체(또는 특정 파일)를 Opus에 보내 결정사항 후보 추출.

```json
Request Body:
{
  "session_ids": ["2026-04-13-session-01"],  // 생략 시 전체
  "include_pinned_weight": true              // mom-level 핀 가중치 반영 여부
}

Response 200 (스트리밍 또는 완료 후):
{
  "candidates": [
    {
      "id": "cand-uuid-5678",
      "content": "추출된 결정사항 요약",
      "context": "배경 및 근거 설명",
      "confidence": 0.92,
      "source_sessions": ["2026-04-13-session-01"],
      "source_quotes": ["원본 발언 인용 1", "원본 발언 인용 2"],
      "is_pinned_mom": false,
      "is_pinned_boss": false
    }
  ],
  "analysis_summary": "이번 분석에서 발견된 패턴 요약",
  "duration_ms": 4200
}
```

**서버 내부 Opus 호출:**
```python
import anthropic

def run_opus_analysis(mom_contents: str, pinned_ids: list[str]) -> dict:
    client = anthropic.Anthropic()
    
    pinned_hint = ""
    if pinned_ids:
        pinned_hint = f"\n\n[중요 힌트] 다음 항목들은 사용자가 중요하다고 표시했습니다: {pinned_ids}"
    
    prompt = f"""다음은 프로젝트 회의/대화 기록(mom MD)입니다.
반복적으로 언급되거나 팀이 명시적으로 동의한 결정사항을 추출하세요.
{pinned_hint}

각 결정사항마다:
1. 한 줄 요약 (content)
2. 배경 및 근거 (context)
3. 원본 발언 인용 (source_quotes)
4. 확신도 0.0~1.0 (confidence)

응답은 JSON 배열로만.

---
{mom_contents}"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text)
```

---

#### POST /api/pin/mom

mom-level 핀 추가/제거 토글. pins.json 업데이트.

```json
Request Body:
{
  "candidate_id": "cand-uuid-5678",
  "action": "toggle"   // "pin" | "unpin" | "toggle"
}

Response 200:
{
  "candidate_id": "cand-uuid-5678",
  "is_pinned": true,
  "total_pinned": 3
}
```

**pins.json 구조:**
```json
{
  "mom_pins": [
    {
      "candidate_id": "cand-uuid-5678",
      "content": "결정사항 요약",
      "pinned_at": "2026-04-13T10:30:00Z"
    }
  ]
}
```

---

#### POST /api/pin/boss

boss-level 확정. decisions.md에 항목 추가 기록.

```json
Request Body:
{
  "candidate_id": "cand-uuid-5678",
  "content": "최종 결정사항 요약 (편집 가능)",
  "context": "배경 및 근거 (편집 가능)"
}

Response 200:
{
  "decision_id": "dec-uuid-1234",
  "content": "최종 결정사항 요약",
  "decisions_md_updated": true
}
```

**decisions.md 추가 형식:**
```markdown
## [2026-04-13] 최종 결정사항 요약

배경 및 근거 내용.

<!-- decision_id: dec-uuid-1234 -->
```

---

#### DELETE /api/pin/boss/{id}

decisions.md에서 특정 결정사항 항목 제거.

```
Path Parameter: id = decision_id (UUID)

Response 200:
{
  "decision_id": "dec-uuid-1234",
  "deleted": true,
  "decisions_md_updated": true
}

Response 404:
{
  "error": "decision_id not found",
  "decision_id": "dec-uuid-1234"
}
```

서버는 `<!-- decision_id: {id} -->` 주석을 기준으로 해당 `##` 섹션 전체를 삭제.

---

### 5.4 UI 레이아웃

**전체 3컬럼 구조:**

```
┌────────────────────────────────────────────────────────────────────┐
│  🐹 Hamstern Dashboard                          [재분석] [?]       │
├──────────────┬──────────────────────────────┬─────────────────────┤
│ 왼쪽 컬럼    │ 가운데 컬럼                  │ 오른쪽 컬럼         │
│ (baby 세션)  │ (분석 결과 카드)             │ (decisions.md)      │
│  200px       │  flex-grow                   │  280px              │
├──────────────┼──────────────────────────────┼─────────────────────┤
│ 세션 목록    │ [Opus 추론 패널 — 접힘/펼침] │ 결정사항 목록       │
│              │                              │                      │
│ • 04-13 ①   │ ┌──────────────────────────┐ │ ┌─────────────────┐ │
│ • 04-12      │ │ 결정사항 후보 카드       │ │ │ 결정사항 #1     │ │
│ • 04-11      │ │                          │ │ │ 내용 요약       │ │
│ ...          │ │ 📌 mom핀  ✅ 확정        │ │ │ 2026-04-13      │ │
│              │ └──────────────────────────┘ │ │ [삭제]          │ │
│              │ ┌──────────────────────────┐ │ └─────────────────┘ │
│              │ │ 결정사항 후보 카드       │ │                      │
│              │ │                          │ │ ┌─────────────────┐ │
│              │ │ 📌 mom핀  ✅ 확정        │ │ │ 결정사항 #2     │ │
│              │ └──────────────────────────┘ │ └─────────────────┘ │
└──────────────┴──────────────────────────────┴─────────────────────┘
```

**왼쪽 컬럼 (200px 고정, 스크롤 가능):**
- 제목: "세션 목록"
- 각 세션: 날짜 + 제목 약칭 + mom-level 핀 개수 뱃지
- 클릭 시 해당 세션 카드만 필터링 (또는 하이라이트)
- 전체 보기 버튼

**가운데 컬럼 (flex-grow, 스크롤 가능):**

상단 툴바:
```
[전체 재분석]  [선택 재분석]    정렬: [확신도▼] [날짜] [핀순]
```

Opus 추론 패널 (재분석 클릭 시 등장, 토글 가능):
```
┌─ Opus 추론 진행 중... ─────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓░░░░  분석 중 (4.2s 경과)                               │
│ "반복 언급 패턴 감지: API 설계 관련 3회..."                     │
└────────────────────────────────────────────────────────────────┘
```
완료 후:
```
┌─ Opus 분석 완료 (6.1s) ───────────────────────────────────────┐
│ 7개 후보 추출 | 신규 4개 | 기존 유지 3개                       │
│ 요약: "API 설계와 모델 선택에 대한 명시적 합의가 다수 발견됨"  │
└────────────────────────────────────────────────────────────────┘
```

결정사항 후보 카드:
```
┌────────────────────────────────────────────────────────────────┐
│ 확신도 ████████░░ 92%                              📌 [mom핀] │
│                                                                │
│ **Approach B: Python 경량 서버 방식 채택**                     │
│                                                                │
│ 배경: Claude가 직접 서버를 실행하는 방식으로, 앱은 파일만 생성 │
│ 하고 서버가 파일을 읽어 API 응답. 브라우저와 서버 간 직접 통신. │
│                                                                │
│ 원본 발언:                                                     │
│ > "서버가 Opus 호출을 담당하고 앱은 파일만 만들면 되지"        │
│                                                                │
│                              [✅ boss 확정] [상세보기]         │
└────────────────────────────────────────────────────────────────┘
```

카드 상태별 스타일:
- 기본: 흰색 배경, 회색 테두리
- mom-level 핀: 노란색 왼쪽 테두리 + 상단 핀 아이콘
- boss-level 확정: 초록색 배경 + 체크 아이콘 (오른쪽 컬럼으로 이동 애니메이션)

**오른쪽 컬럼 (280px 고정, 스크롤 가능):**
- 제목: "확정된 결정사항 ({n}개)"
- decisions.md 실시간 미러링 (5초 폴링 또는 WebSocket)
- 각 항목: 내용 + 날짜 + [삭제] 버튼
- 하단: [decisions.md 열기] 버튼 (파일 직접 오픈)

**컬러 팔레트:**
```
배경: #f8f9fa
카드: #ffffff
mom 핀 강조: #ffd43b (노란색)
boss 확정: #d3f9d8 (연한 초록)
Opus 패널: #e7f5ff (연한 파란색)
확정 버튼: #40c057 (초록)
삭제: #fa5252 (빨간색)
```

---

### 5.5 Opus 추론 프로세스

**입력 데이터 준비:**

```python
def prepare_mom_content(session_ids: list[str] | None, pinned_ids: list[str]) -> str:
    """mom MD 파일을 하나의 문자열로 합산. 핀된 항목에 가중치 태그 삽입."""
    
    files = sorted(MOM_DIR.glob("*.md"), reverse=True)  # 최신 순
    
    if session_ids:
        files = [f for f in files if f.stem in session_ids]
    
    parts = []
    for f in files:
        content = f.read_text(encoding="utf-8")
        
        # 파일 헤더 삽입
        parts.append(f"=== 세션: {f.stem} ===\n{content}\n")
    
    full_content = "\n".join(parts)
    
    # 핀된 항목 가중치 힌트 추가
    if pinned_ids:
        hint = "[중요 힌트] 다음 후보들은 사용자가 중요하다고 표시했습니다. 이와 관련된 맥락을 더 세밀하게 분석하세요:\n"
        hint += "\n".join(f"- {pid}" for pid in pinned_ids)
        full_content = hint + "\n\n" + full_content
    
    return full_content
```

**Opus 프롬프트 구조:**

```
시스템 지시:
당신은 프로젝트 의사결정 분석 전문가입니다.
대화/회의 기록에서 명시적 또는 암묵적 결정사항을 추출합니다.

사용자 프롬프트:
다음 회의/대화 기록(mom MD)에서 결정사항 후보를 추출해주세요.

추출 기준:
1. 2회 이상 반복 언급된 방향성
2. "~하기로 했다", "~로 결정", "~가 맞다" 등 명시적 합의 표현
3. 팀 전체가 동의한 것으로 보이는 접근법
4. [중요 힌트] 섹션에 명시된 항목과 관련된 내용 우선

제외 기준:
- 단순 질문이나 아이디어 제안 (결론 없음)
- 한 사람만 주장하고 동의 없는 의견

응답 형식 (JSON 배열만):
[
  {
    "content": "한 줄 결정사항 요약",
    "context": "배경 및 근거 2~4문장",
    "confidence": 0.0~1.0,
    "source_quotes": ["원본 발언 1", "원본 발언 2"]
  }
]

--- 기록 시작 ---
{full_content}
```

**응답 파싱 및 중복 제거:**

```python
def deduplicate_candidates(new_candidates: list, existing_decisions: list) -> list:
    """기존 decisions.md 항목과 중복되는 후보 필터링."""
    
    existing_contents = [d["content"] for d in existing_decisions]
    
    filtered = []
    for cand in new_candidates:
        # 유사도 체크 (간단한 단어 겹침 기준, 70% 이상이면 중복 간주)
        is_duplicate = any(
            similarity(cand["content"], existing) > 0.7
            for existing in existing_contents
        )
        if not is_duplicate:
            filtered.append(cand)
        else:
            cand["is_duplicate"] = True
            filtered.append(cand)  # 중복이어도 표시는 함 (다른 스타일로)
    
    return filtered

def similarity(a: str, b: str) -> float:
    """단어 집합 Jaccard 유사도."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)
```

**분석 진행 상황 스트리밍 (브라우저 → 서버 폴링):**

```
브라우저: GET /api/analyze/status?job_id=job-uuid-xyz
서버 응답:
{
  "job_id": "job-uuid-xyz",
  "status": "running",       // "pending" | "running" | "done" | "error"
  "elapsed_ms": 3200,
  "progress_message": "mom MD 5개 파일 처리 중..."
}
```

서버는 분석 작업을 별도 스레드로 실행하고 `jobs` 딕셔너리에 상태 저장. 브라우저는 1초 간격으로 폴링.

---

### 5.6 2단계 핀 플로우

**개념 정의:**

| 단계 | 이름 | 의미 | 저장 위치 |
|------|------|------|-----------|
| 1단계 | mom-level 핀 | "중요한데 아직 결정 안 됨 — 다음 Opus 분석 시 가중치 부여" | pins.json |
| 2단계 | boss-level 확정 | "최종 확정 — 이후 모든 세션에서 따를 결정사항" | decisions.md |

---

**mom-level 핀 플로우:**

```
사용자: 카드의 [📌 mom핀] 버튼 클릭
    ↓
브라우저: POST /api/pin/mom
          { "candidate_id": "cand-uuid-5678", "action": "toggle" }
    ↓
서버: pins.json 업데이트
    ↓
서버: Response { "is_pinned": true }
    ↓
브라우저: 카드 노란색 테두리로 변경
          왼쪽 세션 목록 뱃지 숫자 +1
```

**mom-level 핀의 효과:**
- UI에서 핀된 카드 상단 정렬 (선택적)
- 다음 "재분석" 클릭 시 `POST /api/analyze` body에 `include_pinned_weight: true` 포함
- Opus 프롬프트에 핀된 후보의 content가 [중요 힌트]로 삽입
- 핀된 항목이 아직 결정 안 됐다는 신호 → Opus가 관련 맥락 더 깊게 탐색

**pins.json 상태 관리:**
```python
def toggle_mom_pin(candidate_id: str, candidate_content: str) -> bool:
    pins = load_pins()
    
    existing = next((p for p in pins["mom_pins"] if p["candidate_id"] == candidate_id), None)
    
    if existing:
        pins["mom_pins"].remove(existing)
        is_pinned = False
    else:
        pins["mom_pins"].append({
            "candidate_id": candidate_id,
            "content": candidate_content,
            "pinned_at": datetime.utcnow().isoformat() + "Z"
        })
        is_pinned = True
    
    save_pins(pins)
    return is_pinned
```

---

**boss-level 확정 플로우:**

```
사용자: 카드의 [✅ boss 확정] 버튼 클릭
    ↓
브라우저: 인라인 편집 모달 등장
          - content 필드 (편집 가능, 기본값: Opus 추출 요약)
          - context 필드 (편집 가능, 기본값: Opus 추출 근거)
          - [취소] [확정] 버튼
    ↓
사용자: 내용 확인/편집 후 [확정] 클릭
    ↓
브라우저: POST /api/pin/boss
          { "candidate_id": "...", "content": "편집된 내용", "context": "편집된 근거" }
    ↓
서버: decisions.md에 섹션 추가
      ## [2026-04-13] 편집된 내용
      편집된 근거
      <!-- decision_id: dec-uuid-1234 -->
    ↓
서버: Response { "decision_id": "dec-uuid-1234", "decisions_md_updated": true }
    ↓
브라우저:
  - 카드 초록색으로 변경 + "확정됨" 뱃지
  - 오른쪽 컬럼 decisions 목록 갱신 (즉시 폴링)
  - [📌 mom핀] 버튼 비활성화 (이미 확정됨)
```

**boss-level 확정 취소 (삭제) 플로우:**

```
사용자: 오른쪽 컬럼의 결정사항 [삭제] 버튼 클릭
    ↓
브라우저: 확인 다이얼로그
          "결정사항을 삭제하시겠습니까? decisions.md에서 제거됩니다."
    ↓
사용자: [삭제 확인] 클릭
    ↓
브라우저: DELETE /api/pin/boss/{decision_id}
    ↓
서버: decisions.md에서 해당 ## 섹션 삭제
      (<!-- decision_id: {id} --> 주석으로 구간 특정)
    ↓
브라우저:
  - 오른쪽 컬럼에서 해당 항목 제거 (애니메이션)
  - 가운데 컬럼: 해당 카드의 "확정됨" 상태 해제 (다시 boss 확정 가능)
```

---

**전체 상태 전이도:**

```
[새 후보 카드]
      │
      │ [📌 mom핀] 클릭
      ▼
[mom-level 핀됨] ──→ 다음 Opus 분석 시 가중치 부여
      │
      │ [✅ boss 확정] 클릭
      ▼
[boss-level 확정] ──→ decisions.md 기록
      │                오른쪽 컬럼에 표시
      │ [삭제] 클릭
      ▼
[제거됨] ──→ decisions.md에서 삭제
              카드 상태 "후보"로 복귀
```

---

## 관련 스킬

- `hams-context` — decisions.md를 세션에 로드 (대시보드 없이 빠른 컨텍스트 주입)
- `hams-audit-decisions` — 기존 decisions.md 내용 타당성 재검토
- `hams-why` — 개별 결정사항의 근본 원인 분석

## 파일 의존성

| 파일 | 접근 | 설명 |
|------|------|------|
| `.hamstern/mom-hamster/*.md` | 읽기 전용 | mom MD 세션 파일 |
| `.hamstern/boss-hamster/decisions.md` | 읽기/쓰기 | 확정된 결정사항 |
| `.hamstern/boss-hamster/pins.json` | 읽기/쓰기 | mom-level 핀 상태 |
| `skills/dashboard/server/server.py` | 실행 | Python 서버 |
| `skills/dashboard/server/dashboard.html` | 서빙 | 브라우저 UI |
