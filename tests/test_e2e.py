"""End-to-end smoke test: simulates the full workflow without a browser."""

import json
from pathlib import Path
from living_slides.cli import main
from living_slides.server import create_app
from click.testing import CliRunner


async def test_full_workflow(aiohttp_client, tmp_path):
    """Simulate: create HTML -> open editor -> edit visually -> save -> check changelog."""

    # Step 1: Create HTML via CLI
    html_file = tmp_path / "demo.html"
    runner = CliRunner()
    result = runner.invoke(main, ["create", str(html_file)])
    assert result.exit_code == 0
    assert html_file.exists()

    original_content = html_file.read_text(encoding="utf-8")
    assert "<h1>" in original_content

    # Step 2: Start server (simulated via aiohttp test client)
    app = create_app(str(html_file))
    client = await aiohttp_client(app)

    # Step 3: Load HTML (what the browser does on page open)
    resp = await client.get("/api/load")
    assert resp.status == 200
    data = await resp.json()
    assert "html" in data
    assert "Demo" in data["html"]

    # Step 4: Simulate visual edits (user changes title + adds a paragraph)
    edited_html = data["html"].replace(
        "<h1>Demo</h1>",
        "<h1>My Awesome Presentation</h1>"
    ).replace(
        "<p>This page was created by slive. Edit it visually or with AI.</p>",
        '<p>This is an AI-powered slide deck.</p>\n    <p class="highlight">Built with living-slides + Claude Code.</p>'
    )

    # Step 5: Save (what happens when user presses Ctrl+S)
    resp = await client.post("/api/save", json={"html": edited_html, "css": ""})
    assert resp.status == 200
    save_data = await resp.json()
    assert save_data["ok"] is True
    assert save_data["changes_count"] > 0
    assert len(save_data["summary"]) > 0

    # Step 6: Verify HTML file was updated on disk
    updated_content = html_file.read_text(encoding="utf-8")
    assert "My Awesome Presentation" in updated_content
    assert "AI-powered slide deck" in updated_content

    # Step 7: Verify changelog was created
    changelog_path = tmp_path / "demo.changelog.json"
    assert changelog_path.exists()

    changelog = json.loads(changelog_path.read_text(encoding="utf-8"))
    assert changelog["file"] == "demo.html"
    assert len(changelog["changes"]) > 0
    assert len(changelog["summary"]) > 0
    assert "timestamp" in changelog

    # Step 8: Verify diff CLI command reads the changelog
    result = runner.invoke(main, ["diff", str(html_file)])
    assert result.exit_code == 0
    assert "demo.html" in result.output
    assert "Changes" in result.output

    # Print results for visibility
    print(f"\n--- E2E Test Results ---")
    print(f"File: {changelog['file']}")
    print(f"Summary: {changelog['summary']}")
    print(f"Changes count: {len(changelog['changes'])}")
    for c in changelog["changes"]:
        print(f"  [{c['type']}] {c.get('selector', '')}")
    print(f"--- CLI diff output ---")
    print(result.output)
