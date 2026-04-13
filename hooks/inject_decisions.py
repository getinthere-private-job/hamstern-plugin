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
