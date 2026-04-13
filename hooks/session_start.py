"""SessionStart 훅: compact/startup 시 decisions.md → CLAUDE.md 자동 주입
stdin: {"session_id": "...", "source": "startup|resume|clear|compact", "cwd": "..."}
"""
import sys, json
from pathlib import Path

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
