"""CLI entry point for living-slides (slive command)."""

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
    <p>This page was created by slive. Edit it visually or with AI.</p>
</body>
</html>
"""


@click.group()
@click.version_option(version="0.2.0", prog_name="slive")
def main():
    """slive — the iteration loop for AI-generated HTML slide decks.

    Your slides stay. The rest catches up.
    """
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

    from living_slides.server import run_server
    try:
        run_server(str(path), port=port)
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")


@main.command()
@click.argument("filepath")
@click.option("--template", "-t", default=None, help="Content template (run 'slive templates' to list)")
@click.option("--preset", "-p", default=None, help="Visual style preset (run 'slive presets' to list)")
def create(filepath: str, template: str | None, preset: str | None):
    """Create a new HTML file from a template or visual preset.

    Templates pick by content shape (presentation, business, tech).
    Presets pick by visual aesthetic (bold-signal, dark-botanical, terminal-green).
    Pass exactly one of --template or --preset; pass neither for the default empty page.
    """
    if template and preset:
        raise click.UsageError("pass --template OR --preset, not both.")

    path = Path(filepath).resolve()
    if path.exists():
        raise click.UsageError(f"File already exists: {path}")

    title = path.stem.replace("-", " ").replace("_", " ").title()
    path.parent.mkdir(parents=True, exist_ok=True)

    if preset:
        from living_slides.templates import get_preset
        try:
            content = get_preset(preset, title)
        except ValueError as e:
            raise click.BadParameter(str(e), param_hint="--preset")
        path.write_text(content, encoding="utf-8")
    elif template:
        from living_slides.templates import get_template
        try:
            content = get_template(template, title)
        except ValueError as e:
            raise click.BadParameter(str(e), param_hint="--template")
        path.write_text(content, encoding="utf-8")
    else:
        path.write_text(TEMPLATE.format(title=title), encoding="utf-8")

    click.echo(f"Created: {path}")
    click.echo(f"Run 'slive open {filepath}' to edit visually.")


@main.command()
def templates():
    """List available content templates."""
    from living_slides.templates import list_templates
    click.echo("Content templates (--template):")
    for t in list_templates():
        click.echo(f"  {t['name']:<16} - {t['description']}")


@main.command()
def presets():
    """List available visual style presets."""
    from living_slides.templates import list_presets
    click.echo("Visual style presets (--preset):")
    for p in list_presets():
        click.echo(f"  {p['name']:<16} - {p['description']}")
    click.echo("")
    click.echo("More presets are documented in skills/living-slides/references/style-presets.md")
    click.echo("(adapted from zarazhangrui/frontend-slides under MIT) — AI can generate any of them on demand.")


def _print_changelog(data: dict) -> None:
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
        elif ctype in ("element_added", "element_removed"):
            click.echo(f"  [{ctype}] {sel} ({change.get('tag','')})")
        else:
            click.echo(f"  [{ctype}] {sel}")


@main.command()
@click.argument("filepath")
@click.option("--history", "show_history", is_flag=True,
              help="Show every recorded round, not just the latest.")
@click.option("--touched", is_flag=True,
              help="Print just the set of data-oid values touched across history.")
def diff(filepath: str, show_history: bool, touched: bool):
    """Show the changelog from the last visual editing session.

    With --history, prints every recorded round (the cross-round preserve set).
    With --touched, prints just the data-oid values AI must not stomp.
    """
    from living_slides.history import load_history, touched_oids

    path = Path(filepath).resolve()

    if touched:
        oids = sorted(touched_oids(str(path)))
        if not oids:
            click.echo("No touched oids yet (no edit history).")
            return
        click.echo(f"Touched oids ({len(oids)}):")
        for oid in oids:
            click.echo(f"  {oid}")
        return

    if show_history:
        rounds = load_history(str(path))
        if not rounds:
            click.echo(f"No history found for {path.name}")
            return
        for i, round_data in enumerate(rounds, start=1):
            click.echo(f"=== Round {i} ===")
            _print_changelog(round_data)
            click.echo("")
        return

    changelog_path = path.parent / (path.stem + ".changelog.json")
    if not changelog_path.exists():
        click.echo(f"No changelog found for {path.name}")
        click.echo("Edit the file with 'slive open' first.")
        return

    data = json.loads(changelog_path.read_text(encoding="utf-8"))
    _print_changelog(data)


@main.command()
@click.argument("filepath")
@click.option("--strategy", "-s", default="role",
              type=click.Choice(["role", "sequential", "hash"]),
              help="OID generation strategy (default: role)")
@click.option("--dry-run", is_flag=True, help="Print the result instead of writing back")
def adopt(filepath: str, strategy: str, dry_run: bool):
    """Retrofit data-oid attributes into an existing HTML deck.

    Lets decks generated by other tools (frontend-slides, hand-written HTML,
    AI output without oids) join the iteration loop. Idempotent: running it
    twice does nothing the second time.
    """
    from living_slides.adopt import adopt_html

    path = Path(filepath).resolve()
    if not path.exists():
        raise click.UsageError(f"File not found: {path}")

    original = path.read_text(encoding="utf-8")
    adopted = adopt_html(original, strategy=strategy)

    if adopted == original:
        click.echo(f"{path.name}: no changes (already adopted or nothing to tag).")
        return

    added = adopted.count('data-oid="') - original.count('data-oid="')
    if dry_run:
        click.echo(f"{path.name}: would add {added} data-oid attribute(s).")
        click.echo("--- preview (first 60 lines) ---")
        for line in adopted.splitlines()[:60]:
            click.echo(line)
        return

    path.write_text(adopted, encoding="utf-8")
    click.echo(f"{path.name}: added {added} data-oid attribute(s).")


@main.group()
def asset():
    """Manage assets (charts, images, diagrams) for an HTML file."""
    pass


@asset.command("list")
@click.argument("filepath")
def asset_list(filepath: str):
    """List all assets for an HTML file."""
    from living_slides.assets import list_assets, get_assets_dir

    assets = list_assets(filepath)
    assets_dir = get_assets_dir(filepath)
    click.echo(f"Assets directory: {assets_dir}")

    if not assets:
        click.echo("No assets yet.")
        return

    click.echo(f"\n{len(assets)} asset(s):")
    for a in assets:
        size_kb = a["size"] / 1024
        click.echo(f"  {a['name']:<30} {a['type']:<6} {size_kb:>8.1f} KB")


@asset.command("gen-chart")
@click.argument("filepath")
@click.option("--name", required=True, help="Asset name (without extension)")
@click.option("--type", "chart_type", required=True,
              type=click.Choice(["bar", "hbar", "line", "pie", "scatter"]))
@click.option("--data", required=True, help="JSON data string or path to JSON file")
@click.option("--title", default=None, help="Chart title")
@click.option("--theme", default="dark", type=click.Choice(["dark", "light"]))
def asset_gen_chart(filepath: str, name: str, chart_type: str, data: str,
                    title: str | None, theme: str):
    """Generate a chart image using matplotlib.

    Example:
      slive asset gen-chart deck.html --name revenue --type bar \\
        --data '{"labels":["Q1","Q2","Q3"],"values":[100,200,300]}' \\
        --title "Revenue by Quarter"
    """
    from living_slides.assets import generate_chart

    # Data can be inline JSON or a file path
    if Path(data).exists():
        data_dict = json.loads(Path(data).read_text(encoding="utf-8"))
    else:
        data_dict = json.loads(data)

    try:
        rel_path = generate_chart(
            filepath, name, chart_type, data_dict,
            title=title, theme=theme
        )
        click.echo(f"Chart generated: {rel_path}")
        click.echo(f"Embed in HTML: <img src=\"{rel_path}\" alt=\"{title or name}\">")
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@asset.command("import")
@click.argument("filepath")
@click.option("--name", required=True, help="Target asset name (without extension)")
@click.option("--from", "source", required=True, help="Source image path")
def asset_import(filepath: str, name: str, source: str):
    """Import an externally-generated image into the assets directory.

    Example:
      slive asset import deck.html --name hero --from ./my-generated-image.png
    """
    from living_slides.assets import save_external_image

    try:
        rel_path = save_external_image(filepath, name, source)
        click.echo(f"Imported: {rel_path}")
        click.echo(f"Embed in HTML: <img src=\"{rel_path}\">")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
