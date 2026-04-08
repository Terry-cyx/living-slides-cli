"""Tests for asset generation interface."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from htmlcli.cli import main
from htmlcli.assets import get_assets_dir, list_assets, generate_chart, save_external_image


def test_get_assets_dir(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    assets_dir = get_assets_dir(html)
    assert assets_dir.exists()
    assert assets_dir.name == "deck-assets"
    assert assets_dir.parent == tmp_path


def test_list_assets_empty(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    assets = list_assets(html)
    assert assets == []


def test_generate_bar_chart(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    rel_path = generate_chart(
        html, "revenue", "bar",
        {"labels": ["Q1", "Q2", "Q3"], "values": [100, 200, 300]},
        title="Revenue",
    )
    assert "deck-assets" in rel_path
    assert rel_path.endswith("revenue.png")

    # Verify file exists
    full_path = tmp_path / "deck-assets" / "revenue.png"
    assert full_path.exists()
    assert full_path.stat().st_size > 1000  # Non-trivial PNG


def test_generate_line_chart_multi_series(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    rel_path = generate_chart(
        html, "trend", "line",
        {
            "labels": ["Jan", "Feb", "Mar"],
            "series": [
                {"name": "Sales", "values": [10, 20, 30]},
                {"name": "Marketing", "values": [5, 15, 25]},
            ]
        },
    )
    assert Path(tmp_path / "deck-assets" / "trend.png").exists()


def test_generate_pie_chart(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    rel_path = generate_chart(
        html, "breakdown", "pie",
        {"labels": ["A", "B", "C"], "values": [40, 35, 25]},
    )
    assert Path(tmp_path / "deck-assets" / "breakdown.png").exists()


def test_list_assets_after_generation(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    generate_chart(html, "c1", "bar", {"labels": ["a"], "values": [1]})
    generate_chart(html, "c2", "bar", {"labels": ["a"], "values": [1]})

    assets = list_assets(html)
    assert len(assets) == 2
    names = {a["name"] for a in assets}
    assert "c1.png" in names
    assert "c2.png" in names


def test_save_external_image(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    # Create a fake external image
    ext = tmp_path / "external.png"
    ext.write_bytes(b"\x89PNG\r\n\x1a\nfake")

    rel_path = save_external_image(html, "imported", ext)
    assert "deck-assets" in rel_path

    imported = tmp_path / "deck-assets" / "imported.png"
    assert imported.exists()


def test_cli_asset_list_empty(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["asset", "list", str(html)])
    assert result.exit_code == 0
    assert "No assets" in result.output or "deck-assets" in result.output


def test_cli_gen_chart(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    runner = CliRunner()
    data = json.dumps({"labels": ["Q1", "Q2"], "values": [100, 200]})
    result = runner.invoke(main, [
        "asset", "gen-chart", str(html),
        "--name", "test-chart",
        "--type", "bar",
        "--data", data,
        "--title", "Test",
    ])
    assert result.exit_code == 0
    assert "test-chart.png" in result.output

    img = tmp_path / "deck-assets" / "test-chart.png"
    assert img.exists()


def test_cli_asset_import(tmp_path):
    html = tmp_path / "deck.html"
    html.write_text("<p>test</p>", encoding="utf-8")

    ext = tmp_path / "external.png"
    ext.write_bytes(b"\x89PNG\r\n\x1a\nfake")

    runner = CliRunner()
    result = runner.invoke(main, [
        "asset", "import", str(html),
        "--name", "my-img",
        "--from", str(ext),
    ])
    assert result.exit_code == 0

    imported = tmp_path / "deck-assets" / "my-img.png"
    assert imported.exists()
