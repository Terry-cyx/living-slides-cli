from click.testing import CliRunner
from living_slides.cli import main
from pathlib import Path


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "slive" in result.output.lower() or "slides" in result.output.lower()


def test_create_command(tmp_path):
    runner = CliRunner()
    filepath = str(tmp_path / "newpage.html")
    result = runner.invoke(main, ["create", filepath])
    assert result.exit_code == 0
    assert Path(filepath).exists()
    content = Path(filepath).read_text(encoding="utf-8")
    assert "<html" in content.lower()


def test_create_refuses_overwrite(tmp_path):
    filepath = tmp_path / "existing.html"
    filepath.write_text("<p>existing</p>", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["create", str(filepath)])
    assert result.exit_code != 0 or "already exists" in result.output.lower() or "exists" in result.output.lower()


def test_diff_no_changelog(tmp_path):
    filepath = tmp_path / "test.html"
    filepath.write_text("<p>hello</p>", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["diff", str(filepath)])
    assert "no changelog" in result.output.lower() or "not found" in result.output.lower()


def test_diff_with_changelog(tmp_path):
    import json

    filepath = tmp_path / "test.html"
    filepath.write_text("<p>hello</p>", encoding="utf-8")
    changelog = tmp_path / "test.changelog.json"
    changelog.write_text(json.dumps({
        "file": "test.html",
        "timestamp": "2026-04-04T00:00:00",
        "changes": [{"type": "text_edit", "selector": "p", "before": "old", "after": "new"}],
        "summary": "Modified text in 1 element(s)",
    }), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["diff", str(filepath)])
    assert result.exit_code == 0
    assert "text_edit" in result.output or "Modified" in result.output
