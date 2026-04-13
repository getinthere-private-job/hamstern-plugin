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
