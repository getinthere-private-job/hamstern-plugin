# hams-diary 커스텀 레포 지원 설계

**날짜:** 2026-04-13  
**대상 파일:** `skills/diary/SKILL.md`

---

## 배경

현재 `hams-diary` 스킬은 타겟 레포가 `codingspecialist/hamster-diary`로 하드코딩되어 있다. 사용자가 임의의 GitHub Pages 레포에 마크다운 파일을 배포할 수 있도록 레포 주소를 설정 파일로 관리한다.

---

## 핵심 플로우 (변경 없음)

```
MD 파일 입력
    ↓
타겟 레포 clone/pull → /tmp/{repo-name}
    ↓
git worktree 생성 → /tmp/{repo-name}-{id}
    ↓
worktree 안에서 작업 (HTML 변환, posts.json 수정)
    ↓
commit & push
    ↓
PR 생성 & merge
    ↓
worktree 삭제
    ↓
완료
```

---

## 설정 파일

**위치:** `~/.claude/hams-diary.json`

```json
{
  "repo": "https://github.com/owner/repo.git",
  "pagesUrl": "https://owner.github.io/repo/"
}
```

- `repo`: 필수. HTTPS 또는 SSH URL 모두 지원
- `pagesUrl`: 선택. 생략 시 `repo` URL에서 자동 추론

**자동 추론 규칙:**
- `https://github.com/owner/repo.git` → `https://owner.github.io/repo/`
- `git@github.com:owner/repo.git` → `https://owner.github.io/repo/`

---

## 사용법

```bash
# 일반 사용 (기존과 동일)
/hams-diary ./post.md [카테고리]

# 레포 설정/변경
/hams-diary --set-repo https://github.com/myuser/my-blog.git
```

**첫 실행 시 설정 파일 없으면:**
```
설정된 타겟 레포가 없습니다.
배포할 GitHub 레포 URL을 입력해주세요:
> https://github.com/myuser/my-blog.git

저장 완료: ~/.claude/hams-diary.json
계속 진행합니다...
```

---

## 동적으로 결정되는 값

| 항목 | 결정 방식 |
|------|-----------|
| 타겟 레포 URL | `~/.claude/hams-diary.json`의 `repo` |
| 레포명 | URL 파싱으로 추출 (예: `my-blog`) |
| 로컬 clone 경로 | `/tmp/{repo-name}` |
| worktree 경로 | `/tmp/{repo-name}-{id}` |
| 베이스 브랜치 | `git remote show origin`으로 자동 감지 |
| 블로그 URL | `pagesUrl` 또는 자동 추론 |

---

## 스킬 파일 변경 범위

**변경:**
- `description` frontmatter — 하드코딩 URL 제거, 커스텀 레포 지원 명시
- `사용 방법` 섹션 — `--set-repo` 플래그 추가
- `레포 준비` 단계 — 설정 파일 읽기 → URL 파싱 → clone/pull
- 임시 경로 — `/tmp/hamster-diary` → `/tmp/{repo-name}` 동적 생성
- 베이스 브랜치 — `master` 고정 → 자동 감지
- 결과 출력 — 블로그 URL을 설정에서 가져오도록
- 내부 체크리스트 — 설정 파일 읽기/저장 스텝 추가
- 에러 처리 — 설정 파일 미존재 처리 추가

**유지:**
- MD 파싱, HTML 변환 로직 전체
- posts.json 업데이트 방식
- PR 생성 & merge 흐름
- 카테고리/요약/태그 처리

---

## 에러 처리 추가

```
❌ 설정 파일 없음
  ~/.claude/hams-diary.json 이 존재하지 않습니다.
  /hams-diary --set-repo {URL} 로 먼저 설정하세요.

❌ 레포 URL 파싱 실패
  올바른 GitHub URL 형식인지 확인하세요.
  지원: https://github.com/owner/repo.git
        git@github.com:owner/repo.git
```

---

## 6. 훅 시스템

플러그인이 앱 없이도 독립적으로 동작할 수 있도록 Claude Code hooks를 활용한다. 앱이 실행 중이면 폴백 훅은 양보하고, 앱이 없을 때만 baby/mom MD를 직접 기록한다.

---

### 6.1 SessionStart 훅 (CLAUDE.md 자동 주입)

세션이 시작될 때마다 `decisions.md`의 최신 결정사항을 `CLAUDE.md`에 반영한다. `compact` 또는 `startup` 소스일 때만 주입하여 불필요한 파일 I/O를 방지한다.

**트리거 조건:** `source`가 `"compact"` 또는 `"startup"`인 경우

**stdin 구조:**
```json
{
  "session_id": "abc-123",
  "source": "startup | resume | clear | compact",
  "cwd": "/project/path"
}
```

**스크립트 예시 (`hooks/session-start.py`):**
```python
#!/usr/bin/env python3
"""SessionStart 훅: decisions.md → CLAUDE.md 자동 주입"""

import json
import sys
from pathlib import Path

def main():
    payload = json.load(sys.stdin)
    source = payload.get("source", "")

    # compact 또는 startup 시에만 주입
    if source not in ("compact", "startup"):
        sys.exit(0)

    cwd = Path(payload.get("cwd", "."))
    decisions_path = cwd / "boss-hamster" / "decisions.md"
    claude_md_path = cwd / "CLAUDE.md"

    if not decisions_path.exists():
        sys.exit(0)

    decisions_content = decisions_path.read_text(encoding="utf-8")

    # CLAUDE.md에서 기존 decisions 블록 교체 (없으면 append)
    marker_start = "<!-- hamstern:decisions:start -->"
    marker_end = "<!-- hamstern:decisions:end -->"
    injected_block = (
        f"{marker_start}\n"
        f"## 확정된 결정사항 (auto-injected by hamstern)\n\n"
        f"{decisions_content}\n"
        f"{marker_end}"
    )

    if claude_md_path.exists():
        original = claude_md_path.read_text(encoding="utf-8")
        if marker_start in original:
            # 기존 블록 교체
            start_idx = original.index(marker_start)
            end_idx = original.index(marker_end) + len(marker_end)
            updated = original[:start_idx] + injected_block + original[end_idx:]
        else:
            # 파일 끝에 append
            updated = original.rstrip() + "\n\n" + injected_block + "\n"
    else:
        updated = injected_block + "\n"

    claude_md_path.write_text(updated, encoding="utf-8")
    print(f"[hamstern] decisions.md → CLAUDE.md 주입 완료 (source={source})", file=sys.stderr)

if __name__ == "__main__":
    main()
```

---

### 6.2 baby MD 기록 훅 (폴백)

앱이 실행 중이지 않을 때만 동작하는 폴백 훅이다. `UserPromptSubmit`으로 사용자 입력을, `Stop`으로 Claude 응답을 각각 `baby-hamster/session_{session_id}.md`에 append한다.

#### UserPromptSubmit 훅 (사용자 입력 기록)

**stdin 구조:**
```json
{
  "session_id": "abc-123",
  "prompt": "사용자가 입력한 전체 텍스트",
  "cwd": "/project/path"
}
```

**스크립트 예시 (`hooks/user-prompt-submit.py`):**
```python
#!/usr/bin/env python3
"""UserPromptSubmit 훅: 앱 없을 때 사용자 입력을 baby MD에 기록"""

import json
import sys
from datetime import datetime
from pathlib import Path

APP_RUNNING_FLAG = Path.home() / ".hamstern" / ".app-running"

def main():
    # 앱이 실행 중이면 양보
    if APP_RUNNING_FLAG.exists():
        sys.exit(0)

    payload = json.load(sys.stdin)
    session_id = payload.get("session_id", "unknown")
    prompt = payload.get("prompt", "")
    cwd = Path(payload.get("cwd", "."))

    baby_dir = cwd / "baby-hamster"
    baby_dir.mkdir(parents=True, exist_ok=True)
    baby_path = baby_dir / f"session_{session_id}.md"

    # 파일이 없으면 헤더 생성
    if not baby_path.exists():
        header = (
            f"---\n"
            f"session_id: {session_id}\n"
            f"started_at: {datetime.now().isoformat()}\n"
            f"cwd: {cwd}\n"
            f"source: plugin-hook\n"
            f"---\n\n"
        )
        baby_path.write_text(header, encoding="utf-8")

    # Turn 번호 산출 (기존 ## Turn N 개수 기준)
    existing = baby_path.read_text(encoding="utf-8")
    turn_count = existing.count("\n## Turn ") + 1

    entry = f"## Turn {turn_count}\n**User:** {prompt}\n"
    with baby_path.open("a", encoding="utf-8") as f:
        f.write(entry)

    print(f"[hamstern] baby MD 사용자 입력 기록 (session={session_id}, turn={turn_count})", file=sys.stderr)

if __name__ == "__main__":
    main()
```

#### Stop 훅 (Claude 응답 기록)

`transcript_path`로 전달된 JSONL 파일에서 마지막 assistant 응답을 추출하여 기록한다.

**stdin 구조:**
```json
{
  "session_id": "abc-123",
  "transcript_path": "/tmp/claude-transcript-abc-123.jsonl",
  "cwd": "/project/path"
}
```

**스크립트 예시 (`hooks/stop.py`):**
```python
#!/usr/bin/env python3
"""Stop 훅: 앱 없을 때 Claude 응답을 baby MD에 기록"""

import json
import sys
from pathlib import Path

APP_RUNNING_FLAG = Path.home() / ".hamstern" / ".app-running"

def get_last_assistant_message(transcript_path: str) -> str:
    """JSONL transcript에서 마지막 assistant 메시지 추출"""
    path = Path(transcript_path)
    if not path.exists():
        return ""

    last_response = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        role = entry.get("role") or entry.get("type", "")
        if role == "assistant":
            # content가 리스트(블록)일 경우 텍스트만 추출
            content = entry.get("content", "")
            if isinstance(content, list):
                texts = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                last_response = "\n".join(texts)
            else:
                last_response = str(content)

    return last_response

def main():
    # 앱이 실행 중이면 양보
    if APP_RUNNING_FLAG.exists():
        sys.exit(0)

    payload = json.load(sys.stdin)
    session_id = payload.get("session_id", "unknown")
    transcript_path = payload.get("transcript_path", "")
    cwd = Path(payload.get("cwd", "."))

    response_text = get_last_assistant_message(transcript_path)
    if not response_text:
        sys.exit(0)

    baby_path = cwd / "baby-hamster" / f"session_{session_id}.md"
    if not baby_path.exists():
        # UserPromptSubmit이 먼저 생성하지만, 방어적으로 처리
        sys.exit(0)

    with baby_path.open("a", encoding="utf-8") as f:
        f.write(f"**Claude:** {response_text}\n\n")

    print(f"[hamstern] baby MD Claude 응답 기록 (session={session_id})", file=sys.stderr)

if __name__ == "__main__":
    main()
```

---

### 6.3 mom MD 집계

`SessionEnd` 훅 시점에 모든 `baby-hamster/*.md`를 읽어 날짜순으로 병합한 `mom-hamster/diary.md`를 생성한다. 동일 `session_id`가 이미 포함된 경우 덮어쓰지 않고 건너뛴다.

**스크립트 예시 (`hooks/session-end.py`):**
```python
#!/usr/bin/env python3
"""SessionEnd 훅: baby MD → mom MD 집계"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

def parse_frontmatter(text: str) -> dict:
    """간단한 YAML frontmatter 파싱 (--- 블록)"""
    meta = {}
    if not text.startswith("---"):
        return meta
    end = text.index("---", 3)
    for line in text[3:end].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta

def main():
    payload = json.load(sys.stdin)
    cwd = Path(payload.get("cwd", "."))

    baby_dir = cwd / "baby-hamster"
    mom_dir = cwd / "mom-hamster"
    mom_dir.mkdir(parents=True, exist_ok=True)
    mom_path = mom_dir / "diary.md"

    # 기존 mom MD에서 이미 기록된 session_id 수집
    recorded_sessions: set[str] = set()
    if mom_path.exists():
        for match in re.finditer(r"session_id:\s*(\S+)", mom_path.read_text(encoding="utf-8")):
            recorded_sessions.add(match.group(1))

    # baby MD 파일 수집 및 날짜순 정렬
    baby_files = sorted(
        baby_dir.glob("session_*.md"),
        key=lambda p: parse_frontmatter(p.read_text(encoding="utf-8")).get("started_at", "")
    )

    new_entries = []
    for baby_file in baby_files:
        content = baby_file.read_text(encoding="utf-8")
        meta = parse_frontmatter(content)
        session_id = meta.get("session_id", "")

        if session_id in recorded_sessions:
            continue  # 중복 건너뜀

        new_entries.append(content.strip())
        recorded_sessions.add(session_id)

    if not new_entries:
        print("[hamstern] mom MD: 새로운 세션 없음, 스킵", file=sys.stderr)
        sys.exit(0)

    separator = "\n\n---\n\n"
    with mom_path.open("a", encoding="utf-8") as f:
        if mom_path.stat().st_size > 0:
            f.write("\n\n---\n\n")
        f.write(separator.join(new_entries))
        f.write("\n")

    print(f"[hamstern] mom MD 업데이트 완료: {len(new_entries)}개 세션 추가", file=sys.stderr)

if __name__ == "__main__":
    main()
```

---

### 6.4 앱 감지 및 양보 로직

앱 실행 여부는 `~/.hamstern/.app-running` 파일의 존재 여부로 판단한다. 파일이 있으면 플러그인 훅은 MD 기록을 생략하고 앱에 양보한다. `SessionStart` 훅의 CLAUDE.md 주입은 앱 실행 여부와 무관하게 항상 실행한다.

```
~/.hamstern/
└── .app-running        ← 앱 시작 시 생성, 종료 시 삭제
```

**앱 측 구현 책임:**
- 앱 시작 시: `Path("~/.hamstern/.app-running").expanduser().touch()`
- 앱 정상 종료 시: 파일 삭제
- 앱 비정상 종료 시: 파일이 남을 수 있으므로, 훅에서 파일 mtime이 24시간 초과면 stale로 간주하고 무시하는 방어 로직 권장

**stale 파일 방어 예시 (각 훅 공통 적용):**
```python
import time

def is_app_running() -> bool:
    flag = Path.home() / ".hamstern" / ".app-running"
    if not flag.exists():
        return False
    # 24시간 초과 stale 파일은 무시
    age_seconds = time.time() - flag.stat().st_mtime
    return age_seconds < 86400
```

**훅별 앱 감지 동작 요약:**

| 훅 | 앱 실행 중 | 앱 없을 때 |
|----|-----------|-----------|
| `SessionStart` | 항상 실행 (CLAUDE.md 주입) | 항상 실행 |
| `UserPromptSubmit` | skip | baby MD에 사용자 입력 기록 |
| `Stop` | skip | baby MD에 Claude 응답 기록 |
| `SessionEnd` | mom MD 집계만 실행 | mom MD 집계 실행 |

---

### 6.5 settings.json 훅 설정 예시

Claude Code의 `~/.claude/settings.json` 또는 프로젝트별 `.claude/settings.json`에 아래와 같이 훅을 등록한다.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/hamstern-plugin/hooks/session-start.py"
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
            "command": "python3 /path/to/hamstern-plugin/hooks/user-prompt-submit.py"
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
            "command": "python3 /path/to/hamstern-plugin/hooks/stop.py"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/hamstern-plugin/hooks/session-end.py"
          }
        ]
      }
    ]
  }
}
```

**경로 설정 팁:**
- `/path/to/hamstern-plugin`을 실제 플러그인 설치 경로로 교체한다.
- 플러그인 설치 스크립트(`install.sh`)에서 이 경로를 자동으로 설정하는 방식을 권장한다.
- 프로젝트별로 훅을 격리하고 싶다면 `.claude/settings.json`(프로젝트 루트)에 설정한다.

**훅 실행 흐름 요약:**

```
세션 시작
    ↓
SessionStart 훅
  → decisions.md → CLAUDE.md 주입 (source=startup|compact)
    ↓
사용자 입력
    ↓
UserPromptSubmit 훅
  → .app-running 없으면: baby MD에 User 블록 append
    ↓
Claude 응답 완료
    ↓
Stop 훅
  → .app-running 없으면: transcript_path에서 응답 추출 → baby MD에 Claude 블록 append
    ↓
세션 종료
    ↓
SessionEnd 훅
  → 중복 체크 후 baby MD들 → mom MD 병합
```
