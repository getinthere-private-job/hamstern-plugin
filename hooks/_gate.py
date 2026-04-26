"""Project-scoping gate for hamstern plugin hooks.

Plugin hooks fire globally in every Claude Code session. To keep hamstern's
side effects (creating .hamstern/baby-hamster/, writing CLAUDE.md, etc.)
contained to projects the user actually uses hamstern in, every hook must
gate itself with is_hamstern_project() at entry.

Marker: presence of a `.hamstern/` directory in the session cwd, AND
absence of `.hamstern/.disabled` (so users can pause hamstern in a project
without deleting their data).
"""
from pathlib import Path
from typing import Optional


def is_hamstern_project(cwd: Optional[str]) -> bool:
    """Return True if `cwd` looks like a hamstern-active project.

    Active means:
      - `.hamstern/` directory exists at project root
      - `.hamstern/.disabled` does NOT exist (toggle-off marker)

    The `.hamstern/` directory doubles as both data store and activation
    marker — hamstern itself creates it on first use via /hams-start.
    """
    if not cwd:
        return False
    try:
        marker = Path(cwd) / ".hamstern"
        if not marker.is_dir():
            return False
        if (marker / ".disabled").exists():
            return False
        return True
    except (OSError, ValueError):
        return False
