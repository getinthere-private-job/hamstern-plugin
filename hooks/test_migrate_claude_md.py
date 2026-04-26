"""CLAUDE.md 의 hamstern:decisions 마커 블록 일회성 정리 테스트."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from migrate_claude_md import migrate_claude_md


def test_removes_block_and_preserves_other_content():
    with tempfile.TemporaryDirectory() as d:
        claude_md = Path(d) / "CLAUDE.md"
        claude_md.write_text(
            "# 프로젝트 설정\n"
            "사용자 본인 콘텐츠\n"
            "\n"
            "<!-- hamstern:decisions:start -->\n"
            "## 현재 프로젝트 결정사항 (hamstern 자동 주입)\n\n"
            "_업데이트: 2026-04-26T00:00:00_\n\n"
            "- 옛 결정 1\n"
            "- 옛 결정 2\n"
            "<!-- hamstern:decisions:end -->\n"
            "\n"
            "## 기타 섹션\n"
            "유지되어야 함\n",
            encoding="utf-8",
        )
        migrate_claude_md(str(claude_md))
        content = claude_md.read_text(encoding="utf-8")
        assert "hamstern:decisions" not in content
        assert "옛 결정" not in content
        assert "사용자 본인 콘텐츠" in content
        assert "## 기타 섹션" in content
        assert "유지되어야 함" in content
        # 마커 위·아래의 빈 줄도 함께 정리되어 결과가 3개 이상 연속 개행을 갖지 않음
        assert "\n\n\n" not in content


def test_no_markers_is_noop():
    with tempfile.TemporaryDirectory() as d:
        claude_md = Path(d) / "CLAUDE.md"
        original = "# 프로젝트\n\n순수 사용자 콘텐츠\n"
        claude_md.write_text(original, encoding="utf-8")
        before_mtime = claude_md.stat().st_mtime_ns
        migrate_claude_md(str(claude_md))
        # 내용 동일
        assert claude_md.read_text(encoding="utf-8") == original
        # mtime 도 변경 안 됨 (불필요 write 안 함)
        assert claude_md.stat().st_mtime_ns == before_mtime


def test_missing_claude_md_is_silent():
    with tempfile.TemporaryDirectory() as d:
        claude_md = Path(d) / "CLAUDE.md"
        # 파일 없음 — 예외 없이 종료
        migrate_claude_md(str(claude_md))
        assert not claude_md.exists()


def test_removes_multiple_blocks_defensively():
    with tempfile.TemporaryDirectory() as d:
        claude_md = Path(d) / "CLAUDE.md"
        claude_md.write_text(
            "head\n"
            "<!-- hamstern:decisions:start -->\nA\n<!-- hamstern:decisions:end -->\n"
            "middle\n"
            "<!-- hamstern:decisions:start -->\nB\n<!-- hamstern:decisions:end -->\n"
            "tail\n",
            encoding="utf-8",
        )
        migrate_claude_md(str(claude_md))
        content = claude_md.read_text(encoding="utf-8")
        assert "hamstern:decisions" not in content
        assert "A" not in content.replace("tail", "").replace("head", "").replace("middle", "")
        assert "head" in content and "middle" in content and "tail" in content
