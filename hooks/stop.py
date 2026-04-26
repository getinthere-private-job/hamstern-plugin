import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gate import is_hamstern_project


def is_app_running(cwd: str) -> bool:
    import time
    flag = Path(cwd) / ".hamstern" / ".app-running"
    if not flag.exists():
        return False
    return time.time() - flag.stat().st_mtime <= 86400

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
                    content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
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
    cwd = data.get("cwd", ".")
    if not is_hamstern_project(cwd):
        return
    record_stop(
        session_id=data.get("session_id", "unknown"),
        cwd=cwd,
        transcript_path=data.get("transcript_path", ""),
    )

if __name__ == "__main__":
    main()
