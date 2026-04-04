"""CLI entry point for htmlcli."""

from __future__ import annotations

import json
import sys
import threading
import webbrowser
from pathlib import Path

import click


TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, 'Segoe UI', sans-serif;
            max-width: 960px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }}
        h1 {{ color: #1a1a2e; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>This page was created by htmlcli. Edit it visually or with AI.</p>
</body>
</html>
"""


@click.group()
@click.version_option(version="0.1.0")
def main():
    """htmlcli - Visual HTML editor for AI-assisted workflows."""
    pass


@main.command()
@click.argument("filepath")
@click.option("--port", default=8432, help="Server port (default: 8432)")
def open(filepath: str, port: int):
    """Open an HTML file in the visual editor."""
    path = Path(filepath).resolve()
    if not path.exists():
        click.echo(f"Error: File not found: {path}", err=True)
        sys.exit(1)

    click.echo(f"Opening {path.name} in visual editor...")
    click.echo(f"Editor URL: http://127.0.0.1:{port}")
    click.echo("Press Ctrl+C to stop the server.")

    # Open browser after a short delay
    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open(f"http://127.0.0.1:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    from htmlcli.server import run_server
    try:
        run_server(str(path), port=port)
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")


@main.command()
@click.argument("filepath")
def create(filepath: str):
    """Create a new HTML file from template."""
    path = Path(filepath).resolve()
    if path.exists():
        click.echo(f"Error: File already exists: {path}", err=True)
        sys.exit(1)

    title = path.stem.replace("-", " ").replace("_", " ").title()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE.format(title=title), encoding="utf-8")
    click.echo(f"Created: {path}")
    click.echo(f"Run 'htmlcli open {filepath}' to edit visually.")


@main.command()
@click.argument("filepath")
def diff(filepath: str):
    """Show the changelog from the last visual editing session."""
    path = Path(filepath).resolve()
    changelog_path = path.parent / (path.stem + ".changelog.json")

    if not changelog_path.exists():
        click.echo(f"No changelog found for {path.name}")
        click.echo("Edit the file with 'htmlcli open' first.")
        sys.exit(0)

    data = json.loads(changelog_path.read_text(encoding="utf-8"))
    click.echo(f"File: {data['file']}")
    click.echo(f"Time: {data['timestamp']}")
    click.echo(f"Summary: {data['summary']}")
    click.echo(f"Changes ({len(data['changes'])}):")
    for change in data["changes"]:
        ctype = change["type"]
        sel = change.get("selector", "")
        if ctype == "text_edit":
            click.echo(f"  [{ctype}] {sel}: '{change['before']}' -> '{change['after']}'")
        elif ctype == "attribute_change":
            click.echo(f"  [{ctype}] {sel} @{change['attribute']}: '{change['before']}' -> '{change['after']}'")
        elif ctype == "element_added":
            click.echo(f"  [{ctype}] {sel} ({change['tag']})")
        elif ctype == "element_removed":
            click.echo(f"  [{ctype}] {sel} ({change['tag']})")
        else:
            click.echo(f"  [{ctype}] {sel}")


if __name__ == "__main__":
    main()
