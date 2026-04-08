"""Tests for presentation templates — real PPT use cases that HTML must handle."""

import json
from pathlib import Path
import pytest
from click.testing import CliRunner
from htmlcli.cli import main


class TestPresentationTemplate:
    """htmlcli create --template presentation should produce a multi-slide HTML."""

    def test_create_presentation_template(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "deck.html")
        result = runner.invoke(main, ["create", filepath, "--template", "presentation"])
        assert result.exit_code == 0
        content = Path(filepath).read_text(encoding="utf-8")
        # Must have multiple slides
        assert content.count("slide") >= 3

    def test_presentation_has_navigation(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "deck.html")
        result = runner.invoke(main, ["create", filepath, "--template", "presentation"])
        content = Path(filepath).read_text(encoding="utf-8")
        # Must have prev/next navigation
        assert "prev" in content.lower() or "previous" in content.lower()
        assert "next" in content.lower()

    def test_presentation_has_slide_counter(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "deck.html")
        result = runner.invoke(main, ["create", filepath, "--template", "presentation"])
        content = Path(filepath).read_text(encoding="utf-8")
        # Must have slide counter/indicator
        assert "slide-counter" in content or "slideCounter" in content or "current-slide" in content

    def test_presentation_keyboard_navigation(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "deck.html")
        result = runner.invoke(main, ["create", filepath, "--template", "presentation"])
        content = Path(filepath).read_text(encoding="utf-8")
        # Must support arrow key navigation
        assert "ArrowRight" in content or "ArrowLeft" in content or "keydown" in content


class TestBusinessTemplate:
    """htmlcli create --template business should produce a business deck."""

    def test_create_business_template(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "biz.html")
        result = runner.invoke(main, ["create", filepath, "--template", "business"])
        assert result.exit_code == 0
        content = Path(filepath).read_text(encoding="utf-8")
        # Should have typical business sections
        assert "slide" in content.lower()

    def test_business_has_kpi_cards(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "biz.html")
        runner.invoke(main, ["create", filepath, "--template", "business"])
        content = Path(filepath).read_text(encoding="utf-8")
        # KPI metrics section
        assert "kpi" in content.lower() or "metric" in content.lower()

    def test_business_has_chart_placeholder(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "biz.html")
        runner.invoke(main, ["create", filepath, "--template", "business"])
        content = Path(filepath).read_text(encoding="utf-8")
        # Should have chart area
        assert "chart" in content.lower()


class TestTechTemplate:
    """htmlcli create --template tech should produce a technical presentation."""

    def test_create_tech_template(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "tech.html")
        result = runner.invoke(main, ["create", filepath, "--template", "tech"])
        assert result.exit_code == 0
        content = Path(filepath).read_text(encoding="utf-8")
        assert "slide" in content.lower()

    def test_tech_has_code_block(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "tech.html")
        runner.invoke(main, ["create", filepath, "--template", "tech"])
        content = Path(filepath).read_text(encoding="utf-8")
        # Must have syntax-highlighted code blocks
        assert "<code" in content or "<pre" in content

    def test_tech_has_architecture_section(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "tech.html")
        runner.invoke(main, ["create", filepath, "--template", "tech"])
        content = Path(filepath).read_text(encoding="utf-8")
        # Should have architecture/diagram section
        assert "architecture" in content.lower() or "diagram" in content.lower() or "system" in content.lower()

    def test_tech_has_comparison_table(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "tech.html")
        runner.invoke(main, ["create", filepath, "--template", "tech"])
        content = Path(filepath).read_text(encoding="utf-8")
        # Should have a comparison/feature table
        assert "<table" in content


class TestTemplateList:
    """htmlcli templates should list available templates."""

    def test_list_templates(self):
        runner = CliRunner()
        result = runner.invoke(main, ["templates"])
        assert result.exit_code == 0
        assert "presentation" in result.output.lower()
        assert "business" in result.output.lower()
        assert "tech" in result.output.lower()


class TestStylePresets:
    """htmlcli create --preset should produce a styled multi-slide deck with stable data-oid."""

    @pytest.mark.parametrize("preset", ["bold-signal", "dark-botanical", "terminal-green"])
    def test_create_preset(self, tmp_path, preset):
        runner = CliRunner()
        filepath = str(tmp_path / f"{preset}.html")
        result = runner.invoke(main, ["create", filepath, "--preset", preset])
        assert result.exit_code == 0, result.output
        content = Path(filepath).read_text(encoding="utf-8")
        # Multi-slide
        assert content.count('class="slide') >= 4
        # Has stable data-oid on key objects
        assert 'data-oid="s1"' in content
        assert 'data-oid="s1-title"' in content
        # Has nav script
        assert "data-action=\"next\"" in content

    def test_list_presets(self):
        runner = CliRunner()
        result = runner.invoke(main, ["presets"])
        assert result.exit_code == 0
        assert "bold-signal" in result.output
        assert "dark-botanical" in result.output
        assert "terminal-green" in result.output

    def test_template_and_preset_mutually_exclusive(self, tmp_path):
        runner = CliRunner()
        filepath = str(tmp_path / "deck.html")
        result = runner.invoke(main, [
            "create", filepath, "--template", "presentation", "--preset", "bold-signal"
        ])
        assert result.exit_code != 0
        assert "not both" in result.output.lower()
