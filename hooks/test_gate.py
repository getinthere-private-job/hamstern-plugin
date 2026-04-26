"""Tests for the project-scoping gate."""
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

from _gate import is_hamstern_project


def test_returns_true_when_hamstern_dir_exists(tmp_path):
    (tmp_path / ".hamstern").mkdir()
    assert is_hamstern_project(str(tmp_path)) is True


def test_returns_false_when_hamstern_dir_missing(tmp_path):
    assert is_hamstern_project(str(tmp_path)) is False


def test_returns_false_when_hamstern_is_a_file_not_dir(tmp_path):
    (tmp_path / ".hamstern").write_text("oops")
    assert is_hamstern_project(str(tmp_path)) is False


def test_returns_false_when_disabled_marker_present(tmp_path):
    (tmp_path / ".hamstern").mkdir()
    (tmp_path / ".hamstern" / ".disabled").write_text("")
    assert is_hamstern_project(str(tmp_path)) is False


def test_handles_missing_cwd_gracefully():
    assert is_hamstern_project("/nonexistent/path/does/not/exist") is False


def test_handles_empty_string_cwd():
    assert is_hamstern_project("") is False


def test_handles_none_cwd():
    assert is_hamstern_project(None) is False
