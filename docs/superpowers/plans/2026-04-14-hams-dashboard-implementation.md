# hams-dashboard 재설계 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** hams-dashboard 재설계 — Opus 추론 + 2단계 핀 + decisions→CLAUDE.md 자동 주입 + baby/mom 폴백 기록 훅

**Architecture:** Python HTTP 서버(stdlib only)가 대시보드 UI와 Opus 연동을 담당. Claude Code 훅(SessionStart/UserPromptSubmit/Stop)이 CLAUDE.md 자동 주입 및 baby MD 폴백 기록. decisions.md 단일 진실 소스 → CLAUDE.md 마커 교체.

**Tech Stack:** Python 3 (stdlib only: http.server, json, subprocess, pathlib), Vanilla JS (index.html 단일 파일), Bash (훅 스크립트 래퍼), Markdown

**Spec:** `docs/superpowers/specs/2026-04-14-hams-dashboard-redesign.md`

---

## 파일 맵

**신규 생성:**
- `skills/dashboard/server.py` — HTTP 서버 + API + Opus 호출
- `skills/dashboard/static/index.html` — 3컬럼 대시보드 UI (vanilla JS)
- `skills/dashboard/scripts/aggregate.py` — baby MD → mom MD 집계
- `hooks/session-start.py` — CLAUDE.md 자동 주입 훅
- `hooks/user-prompt.py` — baby MD 폴백 기록 훅 (UserPromptSubmit)
- `hooks/stop.py` — baby MD 폴백 기록 훅 (Stop)
- `.claude/settings.json` — 훅 등록

**수정:**
- `skills/dashboard/SKILL.md` — 재설계 반영
- `skills/context/SKILL.md` — CLAUDE.md 주입 + 훅 자동화 추가

---

## Task 1: CLAUDE.md 마커 주입 유틸리티

**Files:**
- Create: `hooks/inject_decisions.py`
- Test: `hooks/test_inject_decisions.py`

- [ ] **Step 1: 테스트 작성**

```python
# hooks/test_inject_decisions.py
import tempfile, os
from pathlib import Path
from inject_decisions import inject_decisions

def test_inject_no_existing_claude_md():
    with tempfile.TemporaryDirectory() as d:
        decisions = Path(d) / "decisions.md"
        claude_md = Path(d) / "CLAUDE.md"
        decisions.write_text("## Architecture\n- 3폴더 구조\n")
        inject_decisions(str(decisions), str(claude_md))
        content = claude_md.read_text()
        assert "<!-- hamstern:decisions:start -->" in content
        assert "3폴더 구조" in content
        assert "<!-- hamstern:decisions:end -->" in content

def test_inject_replaces_existing_block():
    with tempfile.TemporaryDirectory() as d:
        decisions = Path(d) / "decisions.md"
        claude_md = Path(d) / "CLAUDE.md"
        decisions.write_text("## Architecture\n- 새 결정\n")
        claude_md.write_text("# 기존 내용\n\n<!-- hamstern:decisions:start -->\n## 옛날 결정\n<!-- hamstern:decisions:end -->\n\n## 기타\n유지되어야 함\n")
        inject_decisions(str(decisions), str(claude_md))
        content = claude_md.read_text()
        assert "새 결정" in content
        assert "옛날 결정" not in content
        assert "유지되어야 함" in content

def test_inject_appends_to_existing_file():
    with tempfile.TemporaryDirectory() as d:
        decisions = Path(d) / "decisions.md"
        claude_md = Path(d) / "CLAUDE.md"
        decisions.write_text("## UI\n- 3컬럼\n")
        claude_md.write_text("# 프로젝트 설정\n기존 내용\n")
        inject_decisions(str(decisions), str(claude_md))
        content = claude_md.read_text()
        assert "기존 내용" in content
        assert "3컬럼" in content

def test_inject_no_decisions_file_exits_silently():
    with tempfile.TemporaryDirectory() as d:
        inject_decisions(d + "/nonexistent.md", d + "/CLAUDE.md")
        assert not Path(d + "/CLAUDE.md").exists()
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
cd C:/release-test/book/hamstern-plugin/hooks
python3 -m pytest test_inject_decisions.py -v 2>&1 || echo "FAIL expected"
```

Expected: ModuleNotFoundError (inject_decisions 없음)

- [ ] **Step 3: 구현**

```python
# hooks/inject_decisions.py
import re
from pathlib import Path
from datetime import datetime, timezone

START = "<!-- hamstern:decisions:start -->"
END = "<!-- hamstern:decisions:end -->"

def inject_decisions(decisions_path: str, claude_md_path: str) -> None:
    decisions = Path(decisions_path)
    claude_md = Path(claude_md_path)

    if not decisions.exists():
        return

    content = decisions.read_text(encoding="utf-8")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    block = (
        f"{START}\n"
        f"## 현재 프로젝트 결정사항 (hamstern 자동 주입)\n\n"
        f"_업데이트: {ts}_\n\n"
        f"{content.strip()}\n"
        f"{END}"
    )

    if claude_md.exists():
        existing = claude_md.read_text(encoding="utf-8")
        if START in existing:
            updated = re.sub(
                re.escape(START) + r".*?" + re.escape(END),
                block,
                existing,
                flags=re.DOTALL,
            )
            claude_md.write_text(updated, encoding="utf-8")
        else:
            claude_md.write_text(existing.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
    else:
        claude_md.write_text(block + "\n", encoding="utf-8")
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
cd C:/release-test/book/hamstern-plugin/hooks
python3 -m pytest test_inject_decisions.py -v
```

Expected: 4 passed

- [ ] **Step 5: 커밋**

```bash
git add hooks/inject_decisions.py hooks/test_inject_decisions.py
git commit -m "feat: CLAUDE.md 마커 주입 유틸리티"
```

---

## Task 2: SessionStart 훅 (CLAUDE.md 자동 주입)

**Files:**
- Create: `hooks/session_start.py`
- Modify: `.claude/settings.json`

- [ ] **Step 1: 훅 스크립트 작성**

```python
# hooks/session_start.py
"""
SessionStart 훅: compact/startup 시 decisions.md → CLAUDE.md 자동 주입
stdin: {"session_id": "...", "source": "startup|resume|clear|compact", "cwd": "..."}
"""
import sys, json
from pathlib import Path

# 이 파일의 위치로 inject_decisions 임포트
sys.path.insert(0, str(Path(__file__).parent))
from inject_decisions import inject_decisions

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    cwd = Path(data.get("cwd", "."))
    decisions = cwd / ".hamstern" / "boss-hamster" / "decisions.md"
    claude_md = cwd / "CLAUDE.md"

    inject_decisions(str(decisions), str(claude_md))

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: .claude/settings.json 생성**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 skills/dashboard/../../../hooks/session_start.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

실제 경로는 플러그인이 설치된 경로 기준. 플러그인 루트에서 실행된다고 가정:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 hooks/session_start.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: 수동 테스트**

```bash
cd C:/release-test/book/hamstern-plugin
mkdir -p .hamstern/boss-hamster
echo "## Architecture\n- 테스트 결정" > .hamstern/boss-hamster/decisions.md
echo '{"session_id":"test","source":"compact","cwd":"'$(pwd)'"}' | python3 hooks/session_start.py
cat CLAUDE.md
```

Expected: CLAUDE.md에 `<!-- hamstern:decisions:start -->` 블록 포함

- [ ] **Step 4: 커밋**

```bash
git add hooks/session_start.py .claude/settings.json
git commit -m "feat: SessionStart 훅 — CLAUDE.md 자동 주입"
```

---

## Task 3: baby MD 폴백 기록 훅 (UserPromptSubmit + Stop)

**Files:**
- Create: `hooks/user_prompt.py`
- Create: `hooks/stop.py`
- Create: `hooks/test_baby_record.py`

- [ ] **Step 1: 테스트 작성**

```python
# hooks/test_baby_record.py
import tempfile, json
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).parent))

def make_input(session_id, cwd, prompt=None, transcript_path=None):
    d = {"session_id": session_id, "cwd": cwd}
    if prompt: d["prompt"] = prompt
    if transcript_path: d["transcript_path"] = transcript_path
    return json.dumps(d)

def test_user_prompt_creates_baby_file():
    from user_prompt import record_prompt
    with tempfile.TemporaryDirectory() as d:
        record_prompt(session_id="s1", cwd=d, prompt="안녕하세요")
        baby = Path(d) / ".hamstern" / "baby-hamster" / "session_s1.md"
        assert baby.exists()
        content = baby.read_text()
        assert "session_id: s1" in content
        assert "**User:** 안녕하세요" in content

def test_user_prompt_skipped_when_app_running():
    from user_prompt import record_prompt
    with tempfile.TemporaryDirectory() as d:
        app_flag = Path(d) / ".hamstern" / ".app-running"
        app_flag.parent.mkdir(parents=True)
        app_flag.touch()
        record_prompt(session_id="s1", cwd=d, prompt="무시되어야 함")
        baby = Path(d) / ".hamstern" / "baby-hamster" / "session_s1.md"
        assert not baby.exists()

def test_user_prompt_appends_turns():
    from user_prompt import record_prompt
    with tempfile.TemporaryDirectory() as d:
        record_prompt(session_id="s1", cwd=d, prompt="첫 번째")
        record_prompt(session_id="s1", cwd=d, prompt="두 번째")
        baby = Path(d) / ".hamstern" / "baby-hamster" / "session_s1.md"
        content = baby.read_text()
        assert "## Turn 1" in content
        assert "## Turn 2" in content
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
cd C:/release-test/book/hamstern-plugin/hooks
python3 -m pytest test_baby_record.py -v 2>&1 || echo "FAIL expected"
```

- [ ] **Step 3: user_prompt.py 구현**

```python
# hooks/user_prompt.py
import sys, json, re
from pathlib import Path
from datetime import datetime, timezone

def is_app_running(cwd: str) -> bool:
    import time
    flag = Path(cwd) / ".hamstern" / ".app-running"
    if not flag.exists():
        return False
    age = time.time() - flag.stat().st_mtime
    if age > 86400:
        flag.unlink(missing_ok=True)
        return False
    return True

def record_prompt(session_id: str, cwd: str, prompt: str) -> None:
    if is_app_running(cwd):
        return

    baby_dir = Path(cwd) / ".hamstern" / "baby-hamster"
    baby_dir.mkdir(parents=True, exist_ok=True)
    baby = baby_dir / f"session_{session_id}.md"

    if not baby.exists():
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        baby.write_text(
            f"---\nsession_id: {session_id}\nstarted_at: {ts}\ncwd: {cwd}\nsource: plugin-hook\n---\n",
            encoding="utf-8",
        )

    content = baby.read_text(encoding="utf-8")
    turn = len(re.findall(r"^## Turn", content, re.MULTILINE)) + 1
    baby.write_text(content + f"\n## Turn {turn}\n**User:** {prompt}\n", encoding="utf-8")

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    record_prompt(
        session_id=data.get("session_id", "unknown"),
        cwd=data.get("cwd", "."),
        prompt=data.get("prompt", ""),
    )

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: stop.py 구현**

```python
# hooks/stop.py
import sys, json
from pathlib import Path

def is_app_running(cwd: str) -> bool:
    import time
    flag = Path(cwd) / ".hamstern" / ".app-running"
    if not flag.exists():
        return False
    age = time.time() - flag.stat().st_mtime
    return age <= 86400

def record_stop(session_id: str, cwd: str, transcript_path: str) -> None:
    if is_app_running(cwd):
        return

    baby = Path(cwd) / ".hamstern" / "baby-hamster" / f"session_{session_id}.md"
    if not baby.exists():
        return

    last_msg = ""
    if transcript_path and Path(transcript_path).exists():
        try:
            lines = Path(transcript_path).read_text(encoding="utf-8").strip().splitlines()
            msgs = [json.loads(l) for l in lines if l.strip()]
            assistant_msgs = [m for m in msgs if m.get("role") == "assistant"]
            if assistant_msgs:
                content = assistant_msgs[-1].get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        c.get("text", "") for c in content if isinstance(c, dict)
                    )
                last_msg = str(content)[:2000]
        except Exception:
            pass

    with baby.open("a", encoding="utf-8") as f:
        f.write(f"**Claude:** {last_msg}\n")

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    record_stop(
        session_id=data.get("session_id", "unknown"),
        cwd=data.get("cwd", "."),
        transcript_path=data.get("transcript_path", ""),
    )

if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
cd C:/release-test/book/hamstern-plugin/hooks
python3 -m pytest test_baby_record.py -v
```

Expected: 3 passed

- [ ] **Step 6: settings.json에 훅 추가**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "python3 hooks/session_start.py", "timeout": 10}]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "python3 hooks/user_prompt.py"}]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "python3 hooks/stop.py"}]
      }
    ]
  }
}
```

- [ ] **Step 7: 커밋**

```bash
git add hooks/user_prompt.py hooks/stop.py hooks/test_baby_record.py .claude/settings.json
git commit -m "feat: baby MD 폴백 기록 훅 (UserPromptSubmit + Stop)"
```

---

## Task 4: mom MD 집계 스크립트

**Files:**
- Create: `skills/dashboard/scripts/aggregate.py`
- Create: `skills/dashboard/scripts/test_aggregate.py`

- [ ] **Step 1: 테스트 작성**

```python
# skills/dashboard/scripts/test_aggregate.py
import tempfile
from pathlib import Path
from aggregate import aggregate_baby_to_mom

def _make_baby(dir_path, name, session_id, content):
    baby_dir = Path(dir_path) / ".hamstern" / "baby-hamster"
    baby_dir.mkdir(parents=True, exist_ok=True)
    f = baby_dir / name
    f.write_text(f"---\nsession_id: {session_id}\n---\n{content}", encoding="utf-8")
    return f

def test_aggregates_multiple_babies():
    with tempfile.TemporaryDirectory() as d:
        _make_baby(d, "session_a.md", "a", "## Turn 1\n**User:** 안녕\n**Claude:** 응\n")
        _make_baby(d, "session_b.md", "b", "## Turn 1\n**User:** 기록\n**Claude:** 됨\n")
        aggregate_baby_to_mom(d)
        mom = Path(d) / ".hamstern" / "mom-hamster" / "mom.md"
        assert mom.exists()
        content = mom.read_text()
        assert "안녕" in content
        assert "기록" in content

def test_skips_duplicate_sessions():
    with tempfile.TemporaryDirectory() as d:
        _make_baby(d, "session_a.md", "same-id", "첫 번째")
        _make_baby(d, "session_a2.md", "same-id", "중복")
        aggregate_baby_to_mom(d)
        mom = (Path(d) / ".hamstern" / "mom-hamster" / "mom.md").read_text()
        assert mom.count("same-id") == 1
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
cd C:/release-test/book/hamstern-plugin/skills/dashboard/scripts
python3 -m pytest test_aggregate.py -v 2>&1 || echo "FAIL expected"
```

- [ ] **Step 3: 구현**

```python
# skills/dashboard/scripts/aggregate.py
import re
from pathlib import Path
from datetime import datetime, timezone

def aggregate_baby_to_mom(project_root: str) -> None:
    baby_dir = Path(project_root) / ".hamstern" / "baby-hamster"
    mom_file = Path(project_root) / ".hamstern" / "mom-hamster" / "mom.md"
    mom_file.parent.mkdir(parents=True, exist_ok=True)

    if not baby_dir.exists():
        mom_file.write_text("# Mom MD\n\n(baby MD 없음)\n", encoding="utf-8")
        return

    babies = sorted(baby_dir.glob("*.md"), key=lambda f: f.stat().st_mtime)
    seen = set()
    parts = []

    for baby in babies:
        content = baby.read_text(encoding="utf-8")
        m = re.search(r"session_id:\s*(\S+)", content)
        sid = m.group(1) if m else baby.stem
        if sid in seen:
            continue
        seen.add(sid)
        parts.append(f"<!-- source: {baby.name} -->\n{content.strip()}")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    header = f"# Mom MD\n\n_집계: {ts} | {len(parts)}개 세션_\n\n"
    mom_file.write_text(header + "\n\n---\n\n".join(parts), encoding="utf-8")

if __name__ == "__main__":
    import sys
    aggregate_baby_to_mom(sys.argv[1] if len(sys.argv) > 1 else ".")
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
cd C:/release-test/book/hamstern-plugin/skills/dashboard/scripts
python3 -m pytest test_aggregate.py -v
```

Expected: 2 passed

- [ ] **Step 5: 커밋**

```bash
git add skills/dashboard/scripts/aggregate.py skills/dashboard/scripts/test_aggregate.py
git commit -m "feat: baby MD → mom MD 집계 스크립트"
```

---

## Task 5: 대시보드 HTTP 서버 (기본 엔드포인트)

**Files:**
- Create: `skills/dashboard/server.py`

- [ ] **Step 1: server.py 기본 구조 작성**

```python
# skills/dashboard/server.py
"""
hams-dashboard HTTP 서버
사용법: python3 server.py [--port 7777] [--project /path/to/project]
"""
import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# aggregate.py 임포트
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from aggregate import aggregate_baby_to_mom

STATIC_DIR = Path(__file__).parent / "static"

class HamsHandler(BaseHTTPRequestHandler):
    project_root: str = "."

    def log_message(self, fmt, *args):
        pass  # 서버 로그 억제

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, content):
        body = content.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/":
            index = STATIC_DIR / "index.html"
            self._html(index.read_text(encoding="utf-8") if index.exists() else "<h1>index.html 없음</h1>")

        elif path == "/api/mom":
            mom = Path(self.project_root) / ".hamstern" / "mom-hamster" / "mom.md"
            self._json({"content": mom.read_text(encoding="utf-8") if mom.exists() else ""})

        elif path == "/api/decisions":
            d = Path(self.project_root) / ".hamstern" / "boss-hamster" / "decisions.md"
            self._json({"content": d.read_text(encoding="utf-8") if d.exists() else ""})

        elif path == "/api/baby":
            baby_dir = Path(self.project_root) / ".hamstern" / "baby-hamster"
            files = []
            if baby_dir.exists():
                for f in sorted(baby_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
                    files.append({"name": f.name, "content": f.read_text(encoding="utf-8")})
            self._json({"files": files})

        elif path == "/api/analyze/status":
            status_file = Path(self.project_root) / ".hamstern" / ".analyze-status.json"
            if status_file.exists():
                self._json(json.loads(status_file.read_text()))
            else:
                self._json({"status": "idle", "results": []})

        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/api/analyze":
            self._handle_analyze(body)
        elif path == "/api/pin/mom":
            self._handle_mom_pin(body)
        elif path == "/api/pin/boss":
            self._handle_boss_pin(body)
        else:
            self._json({"error": "not found"}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/pin/boss/"):
            decision_id = path[len("/api/pin/boss/"):]
            self._handle_boss_unpin(decision_id)
        else:
            self._json({"error": "not found"}, 404)

    # --- 핸들러 구현 (Task 6, 7에서 채움) ---
    def _handle_analyze(self, body): self._json({"status": "not implemented"}, 501)
    def _handle_mom_pin(self, body): self._json({"status": "not implemented"}, 501)
    def _handle_boss_pin(self, body): self._json({"status": "not implemented"}, 501)
    def _handle_boss_unpin(self, decision_id): self._json({"status": "not implemented"}, 501)


def run(port: int, project_root: str):
    HamsHandler.project_root = project_root
    server = HTTPServer(("127.0.0.1", port), HamsHandler)
    print(f"hams-dashboard: http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7777)
    parser.add_argument("--project", default=".")
    args = parser.parse_args()
    run(args.port, args.project)
```

- [ ] **Step 2: 서버 동작 확인**

```bash
cd C:/release-test/book/hamstern-plugin
python3 skills/dashboard/server.py --port 7777 &
sleep 1
curl -s http://localhost:7777/api/decisions | python3 -m json.tool
kill %1
```

Expected: `{"content": ""}` 또는 decisions.md 내용

- [ ] **Step 3: 커밋**

```bash
git add skills/dashboard/server.py
git commit -m "feat: 대시보드 HTTP 서버 기본 구조 (GET 엔드포인트)"
```

---

## Task 6: 대시보드 UI (index.html)

**Files:**
- Create: `skills/dashboard/static/index.html`

- [ ] **Step 1: index.html 작성**

```html
<!-- skills/dashboard/static/index.html -->
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>🐹 hams-dashboard</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f5f5; height: 100vh; display: flex; flex-direction: column; }
header { background: #1a1a2e; color: white; padding: 12px 20px; display: flex; align-items: center; gap: 12px; }
header h1 { font-size: 18px; }
header .spacer { flex: 1; }
button { cursor: pointer; border: none; border-radius: 6px; padding: 8px 16px; font-size: 14px; }
.btn-primary { background: #4CAF50; color: white; }
.btn-primary:hover { background: #388E3C; }
.btn-secondary { background: #666; color: white; }
.main { display: flex; flex: 1; overflow: hidden; gap: 1px; background: #ddd; }
.col { background: white; overflow-y: auto; padding: 16px; }
.col-baby { width: 200px; flex-shrink: 0; }
.col-mom { flex: 1; }
.col-decisions { width: 280px; flex-shrink: 0; }
.col h2 { font-size: 14px; color: #666; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
.baby-item { padding: 8px; border-radius: 4px; cursor: pointer; font-size: 13px; color: #333; margin-bottom: 4px; border: 1px solid #eee; }
.baby-item:hover { background: #f0f0f0; }
.baby-item.app { border-left: 3px solid #4CAF50; }
.baby-item.hook { border-left: 3px solid #2196F3; }
.card { border: 1px solid #e0e0e0; border-radius: 8px; padding: 14px; margin-bottom: 12px; background: white; }
.card.mom-pinned { background: #FFF9C4; border-color: #F9A825; }
.card.boss-confirmed { border-color: #4CAF50; border-width: 2px; }
.card.conflict { border-color: #F44336; border-width: 2px; }
.card-title { font-weight: 600; font-size: 14px; margin-bottom: 6px; }
.card-category { font-size: 12px; color: #888; margin-bottom: 8px; }
.card-bg { font-size: 13px; color: #555; margin-bottom: 10px; line-height: 1.5; }
.card-actions { display: flex; gap: 8px; }
.card-actions button { font-size: 12px; padding: 4px 10px; }
.btn-mom-pin { background: #FFF9C4; border: 1px solid #F9A825; color: #555; }
.btn-mom-pin.active { background: #F9A825; color: white; }
.btn-boss-pin { background: #E8F5E9; border: 1px solid #4CAF50; color: #2E7D32; }
.btn-boss-pin:hover { background: #4CAF50; color: white; }
.decisions-item { padding: 8px 10px; border-radius: 4px; font-size: 13px; border: 1px solid #e0e0e0; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }
.decisions-item .del { color: #ccc; cursor: pointer; font-size: 16px; }
.decisions-item .del:hover { color: #F44336; }
.analyze-status { padding: 12px; background: #E3F2FD; border-radius: 6px; margin-bottom: 12px; font-size: 13px; }
.analyze-status.running { background: #FFF3E0; }
pre { white-space: pre-wrap; font-size: 12px; color: #444; line-height: 1.6; }
.section-header { font-size: 12px; color: #888; font-weight: 600; margin: 12px 0 6px; text-transform: uppercase; }
</style>
</head>
<body>
<header>
  <span>🐹</span>
  <h1>hams-dashboard</h1>
  <div class="spacer"></div>
  <button class="btn-primary" onclick="runAnalyze()">🔍 재분석</button>
</header>

<div class="main">
  <!-- 왼쪽: baby MD 목록 -->
  <div class="col col-baby">
    <h2>Baby MDs</h2>
    <div id="baby-list"></div>
  </div>

  <!-- 가운데: mom MD + Opus 결과 카드 -->
  <div class="col col-mom">
    <h2>Mom MD + Audit</h2>
    <div id="analyze-status" style="display:none" class="analyze-status"></div>
    <div id="cards"></div>
    <div class="section-header">Mom MD 원문</div>
    <pre id="mom-content"></pre>
  </div>

  <!-- 오른쪽: decisions.md -->
  <div class="col col-decisions">
    <h2>Decisions</h2>
    <div id="decisions-list"></div>
    <div class="section-header" style="margin-top:16px">원문</div>
    <pre id="decisions-content" style="font-size:11px;color:#999;"></pre>
  </div>
</div>

<script>
const momPins = new Set();
let analyzeInterval = null;

async function load() {
  const [mom, decisions, baby] = await Promise.all([
    fetch('/api/mom').then(r => r.json()),
    fetch('/api/decisions').then(r => r.json()),
    fetch('/api/baby').then(r => r.json()),
  ]);

  document.getElementById('mom-content').textContent = mom.content || '(mom MD 없음)';
  document.getElementById('decisions-content').textContent = decisions.content || '(없음)';
  renderDecisions(decisions.content);
  renderBaby(baby.files);
  checkStatus();
}

function renderBaby(files) {
  const el = document.getElementById('baby-list');
  el.innerHTML = files.map(f => {
    const type = f.name.startsWith('surface_') ? 'app' : 'hook';
    return `<div class="baby-item ${type}" title="${f.name}">${f.name.replace(/^(session_|surface_)/, '').substring(0,12)}...<br><small>${type === 'app' ? '🐹 앱' : '🪝 훅'}</small></div>`;
  }).join('');
}

function renderDecisions(content) {
  const el = document.getElementById('decisions-list');
  if (!content) { el.innerHTML = '<p style="color:#999;font-size:13px">결정사항 없음</p>'; return; }
  const items = content.split('\n').filter(l => l.startsWith('- '));
  el.innerHTML = items.map((item, i) => `
    <div class="decisions-item">
      <span>${item.replace(/^- /, '')}</span>
      <span class="del" onclick="deleteDecision(${i})" title="제거">×</span>
    </div>`).join('');
}

function renderCards(results) {
  const el = document.getElementById('cards');
  el.innerHTML = results.map((r, i) => `
    <div class="card ${momPins.has(i) ? 'mom-pinned' : ''}" id="card-${i}">
      <div class="card-category">${r.category || ''}</div>
      <div class="card-title">${r.decision}</div>
      <div class="card-bg">${r.background || ''}</div>
      <div class="card-actions">
        <button class="btn-mom-pin ${momPins.has(i) ? 'active' : ''}" onclick="toggleMomPin(${i})">
          ${momPins.has(i) ? '📌 mom 핀됨' : '📌 mom 핀'}
        </button>
        <button class="btn-boss-pin" onclick="confirmDecision(${i}, ${JSON.stringify(r)})">
          ✅ 확정
        </button>
      </div>
    </div>`).join('');
}

function toggleMomPin(i) {
  momPins.has(i) ? momPins.delete(i) : momPins.add(i);
  fetch('/api/pin/mom', { method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ index: i, pinned: momPins.has(i) }) });
  document.querySelector(`#card-${i}`).className = `card ${momPins.has(i) ? 'mom-pinned' : ''}`;
  document.querySelector(`#card-${i} .btn-mom-pin`).className = `btn-mom-pin ${momPins.has(i) ? 'active' : ''}`;
  document.querySelector(`#card-${i} .btn-mom-pin`).textContent = momPins.has(i) ? '📌 mom 핀됨' : '📌 mom 핀';
}

async function confirmDecision(i, result) {
  await fetch('/api/pin/boss', { method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify(result) });
  document.querySelector(`#card-${i}`).className = 'card boss-confirmed';
  await load();
}

async function deleteDecision(i) {
  if (!confirm('이 결정사항을 제거할까요?')) return;
  await fetch(`/api/pin/boss/${i}`, { method: 'DELETE' });
  await load();
}

async function runAnalyze() {
  const btn = document.querySelector('.btn-primary');
  btn.textContent = '⏳ 분석 중...';
  btn.disabled = true;
  const statusEl = document.getElementById('analyze-status');
  statusEl.style.display = 'block';
  statusEl.className = 'analyze-status running';
  statusEl.textContent = 'Opus가 mom MD를 분석 중입니다...';

  const pinnedItems = [];
  momPins.forEach(i => {
    const card = document.querySelector(`#card-${i} .card-title`);
    if (card) pinnedItems.push(card.textContent);
  });

  await fetch('/api/analyze', { method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ mom_pins: pinnedItems }) });

  analyzeInterval = setInterval(checkStatus, 2000);
}

async function checkStatus() {
  const r = await fetch('/api/analyze/status').then(res => res.json());
  const statusEl = document.getElementById('analyze-status');
  const btn = document.querySelector('.btn-primary');

  if (r.status === 'done' && r.results && r.results.length > 0) {
    statusEl.className = 'analyze-status';
    statusEl.textContent = `✅ 분석 완료 — ${r.results.length}개 결정사항 추출`;
    btn.textContent = '🔍 재분석';
    btn.disabled = false;
    renderCards(r.results);
    if (analyzeInterval) { clearInterval(analyzeInterval); analyzeInterval = null; }
  } else if (r.status === 'running') {
    statusEl.textContent = `⏳ 분석 중... (${Math.round((r.progress || 0) * 100)}%)`;
  }
}

load();
</script>
</body>
</html>
```

- [ ] **Step 2: 서버 실행 후 브라우저 확인**

```bash
cd C:/release-test/book/hamstern-plugin
python3 skills/dashboard/server.py --port 7777 &
start http://localhost:7777
```

Expected: 3컬럼 UI가 브라우저에 표시됨

- [ ] **Step 3: 커밋**

```bash
git add skills/dashboard/static/index.html
git commit -m "feat: 대시보드 3컬럼 UI (index.html)"
```

---

## Task 7: Opus 분석 엔드포인트 + 핀 저장

**Files:**
- Modify: `skills/dashboard/server.py` (\_handle_analyze, \_handle_boss_pin, \_handle_boss_unpin 구현)

- [ ] **Step 1: \_handle_analyze 구현 (server.py에 추가)**

`_handle_analyze` 메서드를 아래로 교체:

```python
def _handle_analyze(self, body):
    import threading, subprocess, time
    mom = Path(self.project_root) / ".hamstern" / "mom-hamster" / "mom.md"
    if not mom.exists():
        self._json({"error": "mom.md 없음"}, 400)
        return

    status_file = Path(self.project_root) / ".hamstern" / ".analyze-status.json"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps({"status": "running", "progress": 0.0, "results": []}))
    self._json({"status": "running"})

    mom_pins = body.get("mom_pins", [])
    project_root = self.project_root

    def run_opus():
        try:
            mom_content = mom.read_text(encoding="utf-8")
            pins_hint = ""
            if mom_pins:
                pins_hint = "## 우선 처리 항목 (사용자가 중요하다고 표시)\n" + "\n".join(f"- {p}" for p in mom_pins) + "\n\n"

            prompt = f"""다음은 프로젝트 개발 대화 기록입니다.
중복을 제거하고 명확한 결정사항만 추출하세요.

{pins_hint}## 전체 대화 기록
{mom_content[:8000]}

## 출력 형식
JSON 배열로만 응답하세요. 다른 텍스트 없이:
[
  {{
    "decision": "결정사항 (단문 명사형)",
    "category": "Architecture|Performance|UI|Testing|Deployment|Other",
    "background": "이 결정의 배경 (1-2문장)",
    "confidence": 0.9
  }}
]

주의: 코드 블록 없이 순수 JSON만 반환."""

            result = subprocess.run(
                ["claude", "--print", "--model", "claude-opus-4-6", prompt],
                capture_output=True, text=True, timeout=120
            )

            status_file.write_text(json.dumps({"status": "running", "progress": 0.5, "results": []}))

            raw = result.stdout.strip()
            # JSON 추출 (코드블록 있을 경우 제거)
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            results = json.loads(raw)

            # Jaccard 유사도 기반 중복 제거
            def jaccard(a, b):
                sa, sb = set(a.lower().split()), set(b.lower().split())
                return len(sa & sb) / len(sa | sb) if sa | sb else 0

            deduped = []
            for r in results:
                if not any(jaccard(r["decision"], d["decision"]) > 0.7 for d in deduped):
                    deduped.append(r)

            status_file.write_text(json.dumps({"status": "done", "progress": 1.0, "results": deduped}))
        except Exception as e:
            status_file.write_text(json.dumps({"status": "error", "error": str(e), "results": []}))

    threading.Thread(target=run_opus, daemon=True).start()
```

- [ ] **Step 2: \_handle_boss_pin 구현**

```python
def _handle_boss_pin(self, body):
    boss_dir = Path(self.project_root) / ".hamstern" / "boss-hamster"
    boss_dir.mkdir(parents=True, exist_ok=True)
    decisions_file = boss_dir / "decisions.md"
    log_file = boss_dir / "decisions-log.md"

    decision = body.get("decision", "")
    category = body.get("category", "Other")
    background = body.get("background", "")
    source = body.get("source_session", "unknown")

    # decisions.md 읽기 및 카테고리별 추가
    content = decisions_file.read_text(encoding="utf-8") if decisions_file.exists() else "# 프로젝트 결정사항\n"
    cat_header = f"## {category}"
    new_item = f"- {decision}"

    if cat_header in content:
        # 카테고리 섹션에 추가
        content = content.replace(
            cat_header,
            cat_header + "\n" + new_item,
            1
        )
    else:
        content = content.rstrip() + f"\n\n{cat_header}\n{new_item}\n"

    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    # 업데이트 타임스탬프 갱신
    import re
    content = re.sub(r"_마지막 업데이트:.*?_\n", f"_마지막 업데이트: {ts}_\n", content)
    if "_마지막 업데이트:" not in content:
        content = content.replace("# 프로젝트 결정사항\n", f"# 프로젝트 결정사항\n\n_마지막 업데이트: {ts}_\n_업데이트 방법: /hams-dashboard에서 핀으로 확정_\n")

    decisions_file.write_text(content, encoding="utf-8")

    # decisions-log.md append
    log_entry = f"\n---\n\n## {ts} | 핀 추가\n- **결정:** {decision}\n- **카테고리:** {category}\n- **배경:** {background}\n- **출처:** mom MD · session {source}\n"
    if not log_file.exists():
        log_file.write_text("# Decisions Log\n<!-- append-only. 수동 편집 금지. -->\n")
    with log_file.open("a", encoding="utf-8") as f:
        f.write(log_entry)

    # CLAUDE.md 주입
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks"))
    try:
        from inject_decisions import inject_decisions
        inject_decisions(str(decisions_file), str(Path(self.project_root) / "CLAUDE.md"))
    except Exception:
        pass

    self._json({"status": "ok"})
```

- [ ] **Step 3: \_handle_boss_unpin 구현**

```python
def _handle_boss_unpin(self, decision_id):
    boss_dir = Path(self.project_root) / ".hamstern" / "boss-hamster"
    decisions_file = boss_dir / "decisions.md"
    log_file = boss_dir / "decisions-log.md"

    if not decisions_file.exists():
        self._json({"error": "decisions.md 없음"}, 404)
        return

    lines = decisions_file.read_text(encoding="utf-8").splitlines()
    items = [l for l in lines if l.startswith("- ")]
    try:
        idx = int(decision_id)
        removed = items[idx]
    except (ValueError, IndexError):
        self._json({"error": "잘못된 인덱스"}, 400)
        return

    # decisions.md에서 해당 항목 제거
    new_content = "\n".join(l for l in lines if l != removed)
    decisions_file.write_text(new_content + "\n", encoding="utf-8")

    # log append
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    log_entry = f"\n---\n\n## {ts} | 핀 제거\n- **결정:** {removed.lstrip('- ')}\n- **제거 이유:** 사용자가 제외 선택\n"
    if log_file.exists():
        with log_file.open("a", encoding="utf-8") as f:
            f.write(log_entry)

    self._json({"status": "ok"})
```

- [ ] **Step 4: 통합 테스트**

```bash
cd C:/release-test/book/hamstern-plugin
mkdir -p .hamstern/{baby-hamster,mom-hamster,boss-hamster}
echo "## Turn 1\n**User:** 3컬럼 레이아웃 쓰자\n**Claude:** 좋아요" > .hamstern/baby-hamster/session_test.md
python3 skills/dashboard/scripts/aggregate.py .
python3 skills/dashboard/server.py --port 7777 &
sleep 1
curl -s -X POST http://localhost:7777/api/pin/boss \
  -H "Content-Type: application/json" \
  -d '{"decision":"3컬럼 레이아웃","category":"UI","background":"Audit 패널 분리","source_session":"test"}' | python3 -m json.tool
cat .hamstern/boss-hamster/decisions.md
kill %1
```

Expected: decisions.md에 "3컬럼 레이아웃" 항목 포함, CLAUDE.md에 마커 블록 포함

- [ ] **Step 5: 커밋**

```bash
git add skills/dashboard/server.py
git commit -m "feat: Opus 분석 + 핀 저장 엔드포인트"
```

---

## Task 8: SKILL.md 업데이트

**Files:**
- Modify: `skills/dashboard/SKILL.md`
- Modify: `skills/context/SKILL.md`

- [ ] **Step 1: skills/dashboard/SKILL.md 재작성**

```markdown
---
name: hams-dashboard
description: Hamstern 대시보드 웹 UI 실행 — mom MD를 Opus로 분석해 결정사항 추출 + 2단계 핀으로 decisions.md 확정
---

# /hams-dashboard

Hamstern 프로젝트 관리 대시보드를 웹 브라우저에서 엽니다.

## 기능

- **Baby MDs** — Claude 세션별 대화 기록 목록 (앱 기록 + 훅 기록 구분)
- **Mom MD + Audit** — Opus가 중복 제거 후 결정사항 카드로 표시
- **Decisions** — 현재 확정된 결정사항 (decisions.md)

## 동작

```bash
/hams-dashboard [--port 7777] [--project .]
```

1. `skills/dashboard/scripts/aggregate.py`로 baby MD → mom MD 집계 (앱 없을 때)
2. `skills/dashboard/server.py` HTTP 서버 백그라운드 시작 (포트 7777)
3. 브라우저 자동 오픈 (`http://localhost:7777`)
4. Opus 비동기 분석 시작

## 2단계 핀

1. **mom 핀 (📌)** — "중요하지만 아직 미결" 표시 → 재분석 시 Opus가 우선 처리
2. **확정 (✅)** — decisions.md 기록 + CLAUDE.md 마커 섹션 자동 업데이트

## 실행 절차

Claude가 직접 실행:

1. 포트 충돌 확인: `lsof -ti:7777 | xargs kill -9 2>/dev/null; true`
2. 앱 없을 때 집계: `python3 skills/dashboard/scripts/aggregate.py {project_root}`
3. 서버 시작: `python3 skills/dashboard/server.py --port 7777 --project {project_root} &`
4. 브라우저 오픈: `start http://localhost:7777` (Windows) / `open http://localhost:7777` (Mac)

## 데이터 소스

- **Baby:** `.hamstern/baby-hamster/*.md`
- **Mom:** `.hamstern/mom-hamster/mom.md`
- **Decisions:** `.hamstern/boss-hamster/decisions.md`
```

- [ ] **Step 2: skills/context/SKILL.md 재작성**

```markdown
---
name: hams-context
description: decisions.md를 CLAUDE.md에 주입 — compact 후 결정사항 복구. SessionStart 훅으로 자동 실행됨.
allowed-tools:
  - Read
  - Bash
---

# /hams-context

프로젝트의 확정된 결정사항을 CLAUDE.md에 주입합니다.
`/clear` 이후나 새 세션 시작 시 실행하세요. (SessionStart 훅 설정 시 자동 실행)

## 동작

1. `.hamstern/boss-hamster/decisions.md` 존재 확인
2. `hooks/inject_decisions.py`로 CLAUDE.md 마커 섹션 업데이트
3. 완료 출력

## 실행

```bash
/hams-context
```

## 출력

```
📌 decisions.md 로드됨 (12개 결정사항)
CLAUDE.md 마커 섹션 업데이트 완료.
이 세션에서는 위 결정사항들을 따릅니다.
```

## decisions.md 없을 때

```
decisions.md 없음.
/hams-dashboard를 먼저 실행해 결정사항을 확정하세요.
```

## 자동화 (훅 설정)

`.claude/settings.json`의 `SessionStart` 훅이 설정되면 compact/재시작 시 자동 실행됩니다.
수동 실행이 필요 없어집니다.

## 실행 절차

Claude가 직접 실행:

```bash
python3 hooks/inject_decisions.py {decisions_path} {claude_md_path}
```

결과 확인 후 결정사항 개수를 세어 출력.
```

- [ ] **Step 3: 커밋**

```bash
git add skills/dashboard/SKILL.md skills/context/SKILL.md
git commit -m "feat: SKILL.md 업데이트 (dashboard 재설계, context 자동화)"
```

---

## Task 9: 최종 검증 및 푸시

- [ ] **Step 1: 전체 테스트 실행**

```bash
cd C:/release-test/book/hamstern-plugin
python3 -m pytest hooks/ skills/dashboard/scripts/ -v
```

Expected: 모든 테스트 통과

- [ ] **Step 2: E2E 시나리오 검증**

```bash
# 1. baby MD 생성 (훅 시뮬레이션)
mkdir -p .hamstern/baby-hamster
cat > .hamstern/baby-hamster/session_demo.md << 'EOF'
---
session_id: demo
started_at: 2026-04-14T10:00:00
source: plugin-hook
---

## Turn 1
**User:** 대시보드 레이아웃을 3컬럼으로 할까요?
**Claude:** 네, 3컬럼이 좋겠습니다. 왼쪽 baby MD, 가운데 audit, 오른쪽 decisions.
EOF

# 2. mom MD 집계
python3 skills/dashboard/scripts/aggregate.py .

# 3. decisions inject 테스트
echo "## Architecture\n- 3컬럼 레이아웃 확정" > .hamstern/boss-hamster/decisions.md
echo '{"session_id":"test","source":"compact","cwd":"'$(pwd)'"}' | python3 hooks/session_start.py
grep "hamstern:decisions:start" CLAUDE.md && echo "✅ CLAUDE.md 주입 성공"

# 4. 서버 시작
python3 skills/dashboard/server.py --port 7777 &
sleep 1
curl -s http://localhost:7777/api/mom | python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ mom API OK' if d['content'] else '❌ mom 비어있음')"
curl -s http://localhost:7777/api/decisions | python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ decisions API OK')"
kill %1
```

- [ ] **Step 3: 임시 테스트 파일 정리**

```bash
rm -rf .hamstern CLAUDE.md 2>/dev/null; true
```

- [ ] **Step 4: 최종 커밋 + 푸시**

```bash
git push origin main
```

---

## 구현 순서 요약

| Task | 내용 | 의존성 |
|------|------|--------|
| 1 | inject_decisions.py | 없음 |
| 2 | SessionStart 훅 | Task 1 |
| 3 | baby MD 훅 | 없음 |
| 4 | aggregate.py | 없음 |
| 5 | server.py 기본 | Task 4 |
| 6 | index.html | Task 5 |
| 7 | Opus + 핀 | Task 5, Task 1 |
| 8 | SKILL.md | Task 5, 6, 7 |
| 9 | 검증 + 푸시 | 모두 |
