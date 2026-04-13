import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
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
