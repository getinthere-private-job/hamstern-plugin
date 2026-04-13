import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from inject_decisions import inject_decisions

def test_inject_no_existing_claude_md():
    with tempfile.TemporaryDirectory() as d:
        decisions = Path(d) / "decisions.md"
        claude_md = Path(d) / "CLAUDE.md"
        decisions.write_text("## Architecture\n- 3폴더 구조\n")
        inject_decisions(str(decisions), str(claude_md))
        content = claude_md.read_text()
        assert "<!-- hamstern:decisions:start -->" in content
        assert "3폴더 구조" in content
        assert "<!-- hamstern:decisions:end -->" in content

def test_inject_replaces_existing_block():
    with tempfile.TemporaryDirectory() as d:
        decisions = Path(d) / "decisions.md"
        claude_md = Path(d) / "CLAUDE.md"
        decisions.write_text("## Architecture\n- 새 결정\n")
        claude_md.write_text("# 기존 내용\n\n<!-- hamstern:decisions:start -->\n## 옛날 결정\n<!-- hamstern:decisions:end -->\n\n## 기타\n유지되어야 함\n")
        inject_decisions(str(decisions), str(claude_md))
        content = claude_md.read_text()
        assert "새 결정" in content
        assert "옛날 결정" not in content
        assert "유지되어야 함" in content

def test_inject_appends_to_existing_file():
    with tempfile.TemporaryDirectory() as d:
        decisions = Path(d) / "decisions.md"
        claude_md = Path(d) / "CLAUDE.md"
        decisions.write_text("## UI\n- 3컬럼\n")
        claude_md.write_text("# 프로젝트 설정\n기존 내용\n")
        inject_decisions(str(decisions), str(claude_md))
        content = claude_md.read_text()
        assert "기존 내용" in content
        assert "3컬럼" in content

def test_inject_no_decisions_file_exits_silently():
    with tempfile.TemporaryDirectory() as d:
        inject_decisions(d + "/nonexistent.md", d + "/CLAUDE.md")
        assert not Path(d + "/CLAUDE.md").exists()
