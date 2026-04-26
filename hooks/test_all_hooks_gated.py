"""Meta-test: 모든 후크는 .hamstern/ 마커가 없을 때 부작용이 없어야 한다."""
import json
import subprocess
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).parent
HOOKS = ["session_start.py", "user_prompt.py", "stop.py"]


def _run(hook_name, payload, cwd):
    return subprocess.run(
        [sys.executable, str(HOOKS_DIR / hook_name)],
        input=json.dumps(payload), text=True, capture_output=True, timeout=10,
        cwd=cwd,
    )


def test_no_hook_creates_artifacts_in_non_hamstern_project(tmp_path):
    payload = {
        "session_id": "meta",
        "source": "startup",
        "cwd": str(tmp_path),
        "prompt": "anything",
        "transcript_path": "",
    }
    for hook in HOOKS:
        result = _run(hook, payload, str(tmp_path))
        assert result.returncode == 0, f"{hook} crashed: {result.stderr}"

    artifacts = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert artifacts == [], (
        f"Hooks created files in non-hamstern project: {artifacts}"
    )


def test_no_hook_runs_when_disabled_marker_present(tmp_path):
    (tmp_path / ".hamstern").mkdir()
    (tmp_path / ".hamstern" / ".disabled").write_text("")
    payload = {
        "session_id": "disabled-test",
        "source": "startup",
        "cwd": str(tmp_path),
        "prompt": "should be ignored",
        "transcript_path": "",
    }
    for hook in HOOKS:
        result = _run(hook, payload, str(tmp_path))
        assert result.returncode == 0, f"{hook} crashed: {result.stderr}"

    # Only .hamstern/ + .disabled should exist; no baby/, no CLAUDE.md
    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / ".hamstern" / "baby-hamster").exists()


def test_user_prompt_records_when_active(tmp_path):
    (tmp_path / ".hamstern").mkdir()
    payload = {
        "session_id": "active-test",
        "cwd": str(tmp_path),
        "prompt": "hello hamstern",
    }
    result = _run("user_prompt.py", payload, str(tmp_path))
    assert result.returncode == 0
    baby = tmp_path / ".hamstern" / "baby-hamster" / "session_active-test.md"
    assert baby.exists()
    assert "hello hamstern" in baby.read_text(encoding="utf-8")


def test_session_start_injects_when_active(tmp_path):
    (tmp_path / ".hamstern" / "boss-hamster").mkdir(parents=True)
    decisions = tmp_path / ".hamstern" / "boss-hamster" / "decisions.md"
    decisions.write_text("# 핵심 결정", encoding="utf-8")
    payload = {"session_id": "x", "source": "startup", "cwd": str(tmp_path)}
    result = _run("session_start.py", payload, str(tmp_path))
    assert result.returncode == 0
    claude_md = tmp_path / "CLAUDE.md"
    assert claude_md.exists()
    assert "핵심 결정" in claude_md.read_text(encoding="utf-8")


def test_session_start_defers_when_app_running(tmp_path):
    (tmp_path / ".hamstern" / "boss-hamster").mkdir(parents=True)
    (tmp_path / ".hamstern" / ".app-running").write_text("")
    decisions = tmp_path / ".hamstern" / "boss-hamster" / "decisions.md"
    decisions.write_text("# Should not be injected by plugin", encoding="utf-8")
    payload = {"session_id": "x", "source": "startup", "cwd": str(tmp_path)}
    result = _run("session_start.py", payload, str(tmp_path))
    assert result.returncode == 0
    # cmux 툴이 실행 중일 땐 플러그인이 양보 — CLAUDE.md 미생성
    assert not (tmp_path / "CLAUDE.md").exists()
