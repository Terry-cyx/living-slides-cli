"""Real-world PPT scenarios: test that living-slides can handle actual presentation editing workflows."""

import json
from pathlib import Path
from click.testing import CliRunner
from living_slides.cli import main
from living_slides.server import create_app


class TestBusinessDeckEditing:
    """Scenario: User creates a business deck, edits KPI values, AI reads changes."""

    async def test_edit_kpi_values(self, aiohttp_client, tmp_path):
        """User updates revenue from $1.2M to $1.5M and churn from 2.1% to 1.8%."""
        runner = CliRunner()
        filepath = tmp_path / "qbr.html"
        runner.invoke(main, ["create", str(filepath), "--template", "business"])

        app = create_app(str(filepath))
        client = await aiohttp_client(app)

        # Load original
        resp = await client.get("/api/load")
        data = await resp.json()
        original = data["html"]

        # Simulate editing KPI values
        edited = original.replace("$1.2M", "$1.5M").replace("2.1%", "1.8%")
        resp = await client.post("/api/save", json={"html": edited, "css": ""})
        result = await resp.json()

        assert result["ok"] is True
        assert result["changes_count"] > 0

        # Verify changelog captured the KPI changes
        changelog = json.loads((tmp_path / "qbr.changelog.json").read_text(encoding="utf-8"))
        all_text = json.dumps(changelog)
        assert "$1.5M" in all_text or "1.5M" in all_text
        assert "1.8%" in all_text

    async def test_add_new_slide_content(self, aiohttp_client, tmp_path):
        """User adds a new section to the business deck."""
        runner = CliRunner()
        filepath = tmp_path / "deck.html"
        runner.invoke(main, ["create", str(filepath), "--template", "business"])

        app = create_app(str(filepath))
        client = await aiohttp_client(app)

        resp = await client.get("/api/load")
        original = (await resp.json())["html"]

        # Add a new team section before the closing nav
        new_section = '<div class="slide"><h2>Team Updates</h2><ul><li>Hired 3 engineers</li><li>New VP of Sales</li></ul></div>'
        edited = original.replace("</body>", f"{new_section}\n</body>")

        resp = await client.post("/api/save", json={"html": edited, "css": ""})
        result = await resp.json()

        assert result["ok"] is True
        assert result["changes_count"] > 0

        # File should contain the new content
        saved = filepath.read_text(encoding="utf-8")
        assert "Team Updates" in saved
        assert "Hired 3 engineers" in saved


class TestTechDeckEditing:
    """Scenario: User creates tech deck, modifies code examples, updates comparison table."""

    async def test_edit_code_block(self, aiohttp_client, tmp_path):
        """User changes the API endpoint code example."""
        runner = CliRunner()
        filepath = tmp_path / "tech.html"
        runner.invoke(main, ["create", str(filepath), "--template", "tech"])

        app = create_app(str(filepath))
        client = await aiohttp_client(app)

        resp = await client.get("/api/load")
        original = (await resp.json())["html"]

        # Change endpoint from /api/users to /api/products
        edited = original.replace("/api/users", "/api/products").replace("get_users", "get_products")

        resp = await client.post("/api/save", json={"html": edited, "css": ""})
        result = await resp.json()

        assert result["ok"] is True
        changelog = json.loads((tmp_path / "tech.changelog.json").read_text(encoding="utf-8"))
        all_text = json.dumps(changelog)
        assert "products" in all_text.lower()

    async def test_edit_comparison_table(self, aiohttp_client, tmp_path):
        """User flips a feature from ❌ to ✅ in the comparison table."""
        runner = CliRunner()
        filepath = tmp_path / "tech.html"
        runner.invoke(main, ["create", str(filepath), "--template", "tech"])

        app = create_app(str(filepath))
        client = await aiohttp_client(app)

        resp = await client.get("/api/load")
        original = (await resp.json())["html"]

        # Change "Competitor B" offline mode from ✅ to ❌
        # Find the offline mode row and change it
        edited = original.replace(
            "<tr><td>Offline mode</td><td>✅</td><td>❌</td><td>✅</td></tr>",
            "<tr><td>Offline mode</td><td>✅</td><td>✅</td><td>✅</td></tr>"
        )

        resp = await client.post("/api/save", json={"html": edited, "css": ""})
        result = await resp.json()

        assert result["ok"] is True
        assert result["changes_count"] > 0


class TestPresentationEditing:
    """Scenario: User creates a presentation, reorganizes content, AI helps refine."""

    async def test_edit_slide_title(self, aiohttp_client, tmp_path):
        """User changes a slide title."""
        runner = CliRunner()
        filepath = tmp_path / "talk.html"
        runner.invoke(main, ["create", str(filepath), "--template", "presentation"])

        app = create_app(str(filepath))
        client = await aiohttp_client(app)

        resp = await client.get("/api/load")
        original = (await resp.json())["html"]

        edited = original.replace("Key Points", "Core Insights")
        resp = await client.post("/api/save", json={"html": edited, "css": ""})
        result = await resp.json()

        assert result["ok"] is True
        changelog = json.loads((tmp_path / "talk.changelog.json").read_text(encoding="utf-8"))
        # Should detect the text change
        text_edits = [c for c in changelog["changes"] if c["type"] == "text_edit"]
        assert len(text_edits) > 0
        found = any("Core Insights" in c.get("after", "") for c in text_edits)
        assert found, f"Expected 'Core Insights' in text edits, got: {text_edits}"

    async def test_add_css_styling(self, aiohttp_client, tmp_path):
        """User adds custom CSS via GrapesJS style panel — should be preserved."""
        runner = CliRunner()
        filepath = tmp_path / "styled.html"
        runner.invoke(main, ["create", str(filepath), "--template", "presentation"])

        app = create_app(str(filepath))
        client = await aiohttp_client(app)

        resp = await client.get("/api/load")
        original = (await resp.json())["html"]

        # GrapesJS sends CSS separately
        custom_css = "h1 { font-size: 4rem; color: #ff6b6b; }"
        resp = await client.post("/api/save", json={"html": original, "css": custom_css})
        result = await resp.json()

        assert result["ok"] is True
        saved = filepath.read_text(encoding="utf-8")
        assert "ff6b6b" in saved
        assert "4rem" in saved


class TestDiffReadability:
    """Changelog must be readable enough for Claude Code to understand user intent."""

    async def test_diff_cli_output_is_informative(self, aiohttp_client, tmp_path):
        """After edits, 'slive diff' should give Claude Code useful context."""
        runner = CliRunner()
        filepath = tmp_path / "review.html"
        runner.invoke(main, ["create", str(filepath), "--template", "business"])

        app = create_app(str(filepath))
        client = await aiohttp_client(app)

        resp = await client.get("/api/load")
        original = (await resp.json())["html"]

        # Multiple edits: change KPI + change action item
        edited = original.replace("$1.2M", "$2.0M").replace(
            "Expand sales team in APAC", "Open Tokyo office"
        )

        await client.post("/api/save", json={"html": edited, "css": ""})

        # Run diff command
        result = runner.invoke(main, ["diff", str(filepath)])
        assert result.exit_code == 0
        assert "Changes" in result.output
        # Should mention the specific changes
        output_lower = result.output.lower()
        assert "2.0m" in output_lower or "$2.0m" in output_lower or "text_edit" in output_lower

    async def test_changelog_json_has_unified_diff(self, aiohttp_client, tmp_path):
        """Changelog JSON should include a unified diff for Claude Code to read."""
        runner = CliRunner()
        filepath = tmp_path / "difftest.html"
        runner.invoke(main, ["create", str(filepath), "--template", "presentation"])

        app = create_app(str(filepath))
        client = await aiohttp_client(app)

        resp = await client.get("/api/load")
        original = (await resp.json())["html"]
        edited = original.replace("Thank You", "Thanks for Listening!")

        await client.post("/api/save", json={"html": edited, "css": ""})

        changelog = json.loads((tmp_path / "difftest.changelog.json").read_text(encoding="utf-8"))
        # Should have a unified diff field
        assert "diff" in changelog
        assert len(changelog["diff"]) > 0
        assert "Thanks for Listening" in changelog["diff"]
