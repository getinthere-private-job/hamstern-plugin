"""CLAUDE.md 의 hamstern:decisions 마커 블록을 일회성 정리.

과거 디자인은 decisions.md 를 CLAUDE.md 에 영구 주입했다. 새 디자인은
CLAUDE.md 를 건드리지 않고 /hams:remind 호출 시점의 세션에만 출력한다.
이 함수는 기존 사용자의 CLAUDE.md 에 남아있을 잔존 마커 블록을 깨끗하게
제거한다 — idempotent. 마커가 없으면 파일을 쓰지 않는다.
"""
import re
import sys
from pathlib import Path

START = "<!-- hamstern:decisions:start -->"
END = "<!-- hamstern:decisions:end -->"

# 마커 블록 + 양쪽에 붙은 빈 줄까지 함께 매치 — 인접 콘텐츠 사이에 \n\n\n 잔재가
# 남지 않도록.
_BLOCK_RE = re.compile(
    r"\n*" + re.escape(START) + r".*?" + re.escape(END) + r"\n*",
    flags=re.DOTALL,
)


def migrate_claude_md(claude_md_path: str) -> None:
    claude_md = Path(claude_md_path)
    if not claude_md.exists():
        return
    existing = claude_md.read_text(encoding="utf-8")
    if START not in existing:
        return
    cleaned = _BLOCK_RE.sub("\n\n", existing)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).rstrip() + "\n"
    claude_md.write_text(cleaned, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: migrate_claude_md.py <CLAUDE.md path>", file=sys.stderr)
        sys.exit(2)
    migrate_claude_md(sys.argv[1])
