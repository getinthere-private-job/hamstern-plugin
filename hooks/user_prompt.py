import sys, json, re
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from _gate import is_hamstern_project, is_noise_command


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

def is_deeptalk_running(cwd: str) -> bool:
    import time
    flag = Path(cwd) / ".hamstern" / ".deeptalk-running"
    if not flag.exists():
        return False
    age = time.time() - flag.stat().st_mtime
    if age > 86400:
        flag.unlink(missing_ok=True)
        return False
    return True

def record_prompt(session_id: str, cwd: str, prompt: str) -> None:
    if is_app_running(cwd) or is_deeptalk_running(cwd):
        return
    if is_noise_command(prompt):
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
    cwd = data.get("cwd", ".")
    if not is_hamstern_project(cwd):
        return
    record_prompt(
        session_id=data.get("session_id", "unknown"),
        cwd=cwd,
        prompt=data.get("prompt", ""),
    )

if __name__ == "__main__":
    main()
