import json
import pytest
from pathlib import Path
from living_slides.server import create_app


@pytest.fixture
def html_file(tmp_path):
    f = tmp_path / "test.html"
    f.write_text("<div><h1>Hello World</h1></div>", encoding="utf-8")
    return f


@pytest.fixture
def app(html_file):
    return create_app(str(html_file))


async def test_load_html(aiohttp_client, app):
    client = await aiohttp_client(app)
    resp = await client.get("/api/load")
    assert resp.status == 200
    data = await resp.json()
    assert "html" in data
    assert "Hello World" in data["html"]


async def test_save_html(aiohttp_client, app, html_file):
    client = await aiohttp_client(app)
    new_html = "<div><h1>Updated</h1></div>"
    resp = await client.post("/api/save", json={"html": new_html, "css": ""})
    assert resp.status == 200
    data = await resp.json()
    assert data["ok"] is True

    # Verify file was updated
    content = html_file.read_text(encoding="utf-8")
    assert "Updated" in content


async def test_save_creates_changelog(aiohttp_client, app, html_file):
    client = await aiohttp_client(app)
    resp = await client.post("/api/save", json={
        "html": "<div><h1>Changed</h1></div>",
        "css": "",
    })
    data = await resp.json()
    assert data["ok"] is True
    assert "summary" in data

    # Check changelog file exists
    changelog_path = html_file.parent / "test.changelog.json"
    assert changelog_path.exists()


async def test_editor_page(aiohttp_client, app):
    client = await aiohttp_client(app)
    resp = await client.get("/")
    assert resp.status == 200
    text = await resp.text()
    assert "grapesjs" in text.lower() or "gjs" in text.lower()
