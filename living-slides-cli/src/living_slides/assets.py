"""Asset management for living-slides — generated images, charts, diagrams.

Convention: for an HTML file `mypage.html`, assets live in `mypage-assets/` directory
next to it. HTML references them as `./mypage-assets/chart1.png`.

This module provides:
- Standard chart generation (via matplotlib, if installed)
- Asset directory management
- Integration helpers for external tools (Python scripts, AI image generators)
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def get_assets_dir(html_path: str | Path) -> Path:
    """Get the assets directory for an HTML file.

    For mypage.html, returns Path('mypage-assets').
    Creates the directory if it doesn't exist.
    """
    html = Path(html_path)
    assets_dir = html.parent / f"{html.stem}-assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    return assets_dir


def list_assets(html_path: str | Path) -> list[dict]:
    """List all assets for an HTML file."""
    assets_dir = get_assets_dir(html_path)
    if not assets_dir.exists():
        return []

    results = []
    for f in sorted(assets_dir.iterdir()):
        if f.is_file():
            results.append({
                "name": f.name,
                "path": str(f),
                "size": f.stat().st_size,
                "type": f.suffix.lstrip(".").lower(),
            })
    return results


def generate_chart(
    html_path: str | Path,
    name: str,
    chart_type: str,
    data: dict,
    title: str | None = None,
    theme: str = "dark",
) -> str:
    """Generate a chart image using matplotlib.

    Args:
        html_path: Path to the HTML file
        name: Asset filename (without extension)
        chart_type: One of 'bar', 'line', 'pie', 'scatter', 'hbar'
        data: Data dict. For bar/line: {'labels': [...], 'values': [...]}.
              For multi-series: {'labels': [...], 'series': [{'name': 'X', 'values': [...]}, ...]}
              For pie: {'labels': [...], 'values': [...]}
              For scatter: {'x': [...], 'y': [...]}
        title: Optional chart title
        theme: 'dark' or 'light'

    Returns:
        Relative path to the generated image (for HTML <img src="...">)
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError(
            "matplotlib not installed. Run: uv add matplotlib"
        ) from e

    assets_dir = get_assets_dir(html_path)
    out_path = assets_dir / f"{name}.png"

    # Theme colors
    if theme == "dark":
        bg = "#0A0A0A"
        fg = "#FAFAFA"
        muted = "#A1A1AA"
        grid = "#27272A"
        primary = "#6366F1"
        colors = ["#6366F1", "#EC4899", "#F59E0B", "#10B981", "#3B82F6"]
    else:
        bg = "#FAFAFA"
        fg = "#18181B"
        muted = "#52525B"
        grid = "#E4E4E7"
        primary = "#6366F1"
        colors = ["#6366F1", "#EC4899", "#F59E0B", "#10B981", "#3B82F6"]

    plt.rcParams.update({
        "figure.facecolor": bg,
        "axes.facecolor": bg,
        "axes.edgecolor": grid,
        "axes.labelcolor": fg,
        "axes.titlecolor": fg,
        "xtick.color": muted,
        "ytick.color": muted,
        "text.color": fg,
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Arial", "DejaVu Sans"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": grid,
        "grid.alpha": 0.3,
    })

    fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

    if chart_type == "bar":
        labels = data["labels"]
        if "series" in data:
            import numpy as np
            x = np.arange(len(labels))
            n_series = len(data["series"])
            width = 0.8 / n_series
            for i, s in enumerate(data["series"]):
                ax.bar(x + i * width - 0.4 + width/2, s["values"],
                       width, label=s["name"], color=colors[i % len(colors)])
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend(loc="best", frameon=False)
        else:
            ax.bar(labels, data["values"], color=primary)

    elif chart_type == "hbar":
        labels = data["labels"]
        ax.barh(labels, data["values"], color=primary)
        ax.invert_yaxis()

    elif chart_type == "line":
        labels = data["labels"]
        if "series" in data:
            for i, s in enumerate(data["series"]):
                ax.plot(labels, s["values"], label=s["name"],
                        color=colors[i % len(colors)], linewidth=2.5, marker="o")
            ax.legend(loc="best", frameon=False)
        else:
            ax.plot(labels, data["values"], color=primary, linewidth=2.5, marker="o")
            ax.fill_between(range(len(labels)), data["values"], alpha=0.15, color=primary)

    elif chart_type == "pie":
        ax.pie(data["values"], labels=data["labels"], colors=colors,
               autopct="%1.0f%%", startangle=90,
               textprops={"color": fg, "fontsize": 11})
        ax.axis("equal")

    elif chart_type == "scatter":
        ax.scatter(data["x"], data["y"], color=primary, alpha=0.7, s=60)

    else:
        raise ValueError(f"Unknown chart type: {chart_type}. Supported: bar, hbar, line, pie, scatter")

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=16)

    ax.grid(True, axis="y" if chart_type != "hbar" else "x")

    plt.tight_layout()
    plt.savefig(out_path, facecolor=bg, dpi=120, bbox_inches="tight")
    plt.close(fig)

    # Return relative path for HTML embedding
    return f"./{assets_dir.name}/{name}.png"


def save_external_image(
    html_path: str | Path,
    name: str,
    source_path: str | Path,
) -> str:
    """Copy an externally-generated image into the assets directory.

    Use this when you've generated an image with an external tool
    (AI generator, custom Python script, etc.) and want to register it
    as an asset for the HTML file.

    Returns the relative path for HTML embedding.
    """
    import shutil

    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Source image not found: {source}")

    assets_dir = get_assets_dir(html_path)
    ext = source.suffix or ".png"
    dest = assets_dir / f"{name}{ext}"
    shutil.copy2(source, dest)

    return f"./{assets_dir.name}/{dest.name}"


def render_mermaid(
    html_path: str | Path,
    name: str,
    mermaid_source: str,
) -> str:
    """Render a mermaid diagram to SVG using the mermaid-cli (mmdc) if available.

    Falls back to embedding the mermaid source as a <pre class="mermaid"> block
    if mmdc is not installed — in that case, the HTML should include mermaid.js
    from CDN to render client-side.

    Returns either a path to the SVG or a placeholder indicator.
    """
    assets_dir = get_assets_dir(html_path)
    source_file = assets_dir / f"{name}.mmd"
    svg_file = assets_dir / f"{name}.svg"

    source_file.write_text(mermaid_source, encoding="utf-8")

    # Try to render with mmdc
    try:
        result = subprocess.run(
            ["mmdc", "-i", str(source_file), "-o", str(svg_file), "-b", "transparent"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and svg_file.exists():
            return f"./{assets_dir.name}/{svg_file.name}"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: return the .mmd path — caller should use client-side mermaid.js
    return f"./{assets_dir.name}/{source_file.name}"
