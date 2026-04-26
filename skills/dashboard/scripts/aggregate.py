import os
import re
import tempfile
from pathlib import Path
from datetime import datetime, timezone


def _atomic_write(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(target.parent), prefix=".mom.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(target))
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def aggregate_baby_to_mom(project_root: str) -> None:
    baby_dir = Path(project_root) / ".hamstern" / "baby-hamster"
    mom_file = Path(project_root) / ".hamstern" / "mom-hamster" / "mom.md"

    if not baby_dir.exists():
        _atomic_write(mom_file, "# Mom MD\n\n(baby MD 없음)\n")
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
    _atomic_write(mom_file, header + "\n\n---\n\n".join(parts))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python3 aggregate.py <project_root>", file=sys.stderr)
        sys.exit(2)
    aggregate_baby_to_mom(sys.argv[1])
