"""SessionStart 훅: compact/startup 시 decisions.md → CLAUDE.md 자동 주입
stdin: {"session_id": "...", "source": "startup|resume|clear|compact", "cwd": "..."}
"""
import sys, json, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from inject_decisions import inject_decisions
from _gate import is_hamstern_project


def is_app_running(cwd: str) -> bool:
    flag = Path(cwd) / ".hamstern" / ".app-running"
    if not flag.exists():
        return False
    return time.time() - flag.stat().st_mtime <= 86400


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    cwd = data.get("cwd", ".")
    if not is_hamstern_project(cwd):
        return
    if is_app_running(cwd):
        return  # cmux 툴이 이미 처리 중 — 양보
    decisions = Path(cwd) / ".hamstern" / "boss-hamster" / "decisions.md"
    claude_md = Path(cwd) / "CLAUDE.md"
    inject_decisions(str(decisions), str(claude_md))

if __name__ == "__main__":
    main()
