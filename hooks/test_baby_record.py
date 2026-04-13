import tempfile, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

def test_user_prompt_creates_baby_file():
    from user_prompt import record_prompt
    with tempfile.TemporaryDirectory() as d:
        record_prompt(session_id="s1", cwd=d, prompt="안녕하세요")
        baby = Path(d) / ".hamstern" / "baby-hamster" / "session_s1.md"
        assert baby.exists()
        content = baby.read_text()
        assert "session_id: s1" in content
        assert "**User:** 안녕하세요" in content

def test_user_prompt_skipped_when_app_running():
    from user_prompt import record_prompt
    import time
    with tempfile.TemporaryDirectory() as d:
        app_flag = Path(d) / ".hamstern" / ".app-running"
        app_flag.parent.mkdir(parents=True)
        app_flag.touch()
        record_prompt(session_id="s1", cwd=d, prompt="무시되어야 함")
        baby = Path(d) / ".hamstern" / "baby-hamster" / "session_s1.md"
        assert not baby.exists()

def test_user_prompt_appends_turns():
    from user_prompt import record_prompt
    with tempfile.TemporaryDirectory() as d:
        record_prompt(session_id="s1", cwd=d, prompt="첫 번째")
        record_prompt(session_id="s1", cwd=d, prompt="두 번째")
        baby = Path(d) / ".hamstern" / "baby-hamster" / "session_s1.md"
        content = baby.read_text()
        assert "## Turn 1" in content
        assert "## Turn 2" in content
