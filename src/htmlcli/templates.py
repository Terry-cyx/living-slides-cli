"""Presentation templates for htmlcli — real-world PPT replacement scenarios.

Two registries:
- TEMPLATES — content-oriented decks (presentation, business, tech). Pick by content shape.
- PRESETS — visual style decks (bold-signal, dark-botanical, terminal-green). Pick by aesthetic.

Presets are adapted from zarazhangrui/frontend-slides (MIT) STYLE_PRESETS.md;
the full 12-preset catalog lives in skills/htmlcli/references/style-presets.md and
AI can generate any of them on demand. Built-in presets are the curated subset
that ships ready-to-edit.
"""

from __future__ import annotations

TEMPLATES: dict[str, dict] = {}
PRESETS: dict[str, dict] = {}


def _register(name: str, description: str, builder):
    TEMPLATES[name] = {"description": description, "builder": builder}


def _register_preset(name: str, description: str, builder):
    PRESETS[name] = {"description": description, "builder": builder}


def get_template(name: str, title: str) -> str:
    if name not in TEMPLATES:
        raise ValueError(f"Unknown template: {name}. Available: {', '.join(TEMPLATES)}")
    return TEMPLATES[name]["builder"](title)


def get_preset(name: str, title: str) -> str:
    if name not in PRESETS:
        raise ValueError(f"Unknown preset: {name}. Available: {', '.join(PRESETS)}")
    return PRESETS[name]["builder"](title)


def list_templates() -> list[dict]:
    return [{"name": k, "description": v["description"]} for k, v in TEMPLATES.items()]


def list_presets() -> list[dict]:
    return [{"name": k, "description": v["description"]} for k, v in PRESETS.items()]


# ─── Slide navigation script (shared by all presentation templates) ───


SLIDE_NAV_SCRIPT = """\
<script>
(function() {
    const slides = document.querySelectorAll('.slide');
    const counter = document.getElementById('slide-counter');
    let current = 0;

    function showSlide(n) {
        slides.forEach((s, i) => {
            s.style.display = i === n ? 'flex' : 'none';
        });
        current = n;
        if (counter) counter.textContent = (current + 1) + ' / ' + slides.length;
    }

    function nextSlide() { if (current < slides.length - 1) showSlide(current + 1); }
    function prevSlide() { if (current > 0) showSlide(current - 1); }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); nextSlide(); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); prevSlide(); }
    });

    document.querySelectorAll('[data-action="next"]').forEach(b => b.addEventListener('click', nextSlide));
    document.querySelectorAll('[data-action="prev"]').forEach(b => b.addEventListener('click', prevSlide));

    showSlide(0);
})();
</script>
"""


SLIDE_NAV_CONTROLS = """\
<div class="slide-nav">
    <button data-action="prev" class="nav-btn">&#9664; Previous</button>
    <span id="slide-counter" class="slide-counter">1 / 1</span>
    <button data-action="next" class="nav-btn">Next &#9654;</button>
</div>
"""


SLIDE_BASE_CSS = """\
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; }
    .slide {
        width: 100vw; height: 100vh;
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        padding: 4rem 6rem;
        position: relative;
    }
    .slide-nav {
        position: fixed; bottom: 20px; left: 50%;
        transform: translateX(-50%);
        display: flex; align-items: center; gap: 1rem;
        z-index: 100; background: rgba(13,17,23,0.9);
        padding: 8px 16px; border-radius: 8px;
        border: 1px solid #30363d;
    }
    .nav-btn {
        background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
        padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 14px;
    }
    .nav-btn:hover { background: #30363d; }
    .slide-counter { color: #8b949e; font-size: 14px; min-width: 60px; text-align: center; }
    h1 { font-size: 3rem; color: #58a6ff; margin-bottom: 1rem; }
    h2 { font-size: 2rem; color: #79c0ff; margin-bottom: 1rem; }
    h3 { font-size: 1.4rem; color: #d2a8ff; margin-bottom: 0.8rem; }
    p { font-size: 1.2rem; line-height: 1.6; color: #8b949e; }
    ul { list-style: none; padding: 0; }
    ul li { padding: 0.4rem 0; font-size: 1.1rem; }
    ul li::before { content: "→ "; color: #58a6ff; }
"""


# ─── Template: Presentation (generic multi-slide) ───


def _build_presentation(title: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{SLIDE_BASE_CSS}
    .subtitle {{ font-size: 1.5rem; color: #8b949e; }}
</style>
</head>
<body>

<div class="slide" style="background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);">
    <h1>{title}</h1>
    <p class="subtitle">Created with htmlcli + Claude Code</p>
</div>

<div class="slide">
    <h2>Agenda</h2>
    <ul>
        <li>Introduction</li>
        <li>Key Points</li>
        <li>Summary &amp; Next Steps</li>
    </ul>
</div>

<div class="slide">
    <h2>Key Points</h2>
    <p>Add your content here. Edit visually with htmlcli or let AI refine it.</p>
</div>

<div class="slide">
    <h2>Thank You</h2>
    <p>Questions?</p>
</div>

{SLIDE_NAV_CONTROLS}
{SLIDE_NAV_SCRIPT}
</body>
</html>
"""


_register("presentation", "Generic multi-slide presentation with navigation", _build_presentation)


# ─── Template: Business (QBR / KPI deck) ───


def _build_business(title: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{SLIDE_BASE_CSS}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; width: 100%; max-width: 1000px; }}
    .kpi-card {{
        background: #161b22; border: 1px solid #30363d; border-radius: 12px;
        padding: 1.5rem; text-align: center;
    }}
    .kpi-value {{ font-size: 2.5rem; font-weight: 700; color: #58a6ff; }}
    .kpi-label {{ font-size: 0.9rem; color: #8b949e; margin-top: 0.5rem; }}
    .kpi-delta {{ font-size: 0.85rem; margin-top: 0.3rem; }}
    .kpi-delta.up {{ color: #3fb950; }}
    .kpi-delta.down {{ color: #f85149; }}
    .metric {{ font-weight: 600; }}
    .chart-area {{
        width: 100%; max-width: 800px; height: 300px;
        background: #161b22; border: 1px solid #30363d; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        color: #484f58; font-size: 1.1rem; margin-top: 1.5rem;
    }}
    .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; width: 100%; max-width: 1000px; }}
    .swot-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; width: 100%; max-width: 800px; }}
    .swot-card {{ padding: 1.5rem; border-radius: 8px; }}
    .swot-s {{ background: #23863622; border: 1px solid #238636; }}
    .swot-w {{ background: #f8514922; border: 1px solid #f85149; }}
    .swot-o {{ background: #1f6feb22; border: 1px solid #1f6feb; }}
    .swot-t {{ background: #f0883e22; border: 1px solid #f0883e; }}
</style>
</head>
<body>

<div class="slide" style="background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);">
    <h1>{title}</h1>
    <p>Quarterly Business Review</p>
</div>

<div class="slide">
    <h2>Key Metrics</h2>
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value metric">$1.2M</div>
            <div class="kpi-label">Revenue</div>
            <div class="kpi-delta up">▲ 12%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value metric">$85K</div>
            <div class="kpi-label">MRR</div>
            <div class="kpi-delta up">▲ 8%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value metric">2.1%</div>
            <div class="kpi-label">Churn</div>
            <div class="kpi-delta down">▼ 0.3%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value metric">72</div>
            <div class="kpi-label">NPS</div>
            <div class="kpi-delta up">▲ 5</div>
        </div>
    </div>
</div>

<div class="slide">
    <h2>Revenue Trend</h2>
    <div class="chart-area">📊 Chart placeholder — replace with live chart or image</div>
    <div class="two-col" style="margin-top: 1.5rem;">
        <div>
            <h3>Highlights</h3>
            <ul>
                <li>Q4 exceeded target by 15%</li>
                <li>Enterprise segment grew 22%</li>
            </ul>
        </div>
        <div>
            <h3>Action Items</h3>
            <ul>
                <li>Expand sales team in APAC</li>
                <li>Launch mid-market pricing tier</li>
            </ul>
        </div>
    </div>
</div>

<div class="slide">
    <h2>SWOT Analysis</h2>
    <div class="swot-grid">
        <div class="swot-card swot-s"><h3>Strengths</h3><ul><li>Strong brand</li><li>Low churn</li></ul></div>
        <div class="swot-card swot-w"><h3>Weaknesses</h3><ul><li>Limited APAC presence</li><li>Slow onboarding</li></ul></div>
        <div class="swot-card swot-o"><h3>Opportunities</h3><ul><li>AI integration</li><li>Partner channel</li></ul></div>
        <div class="swot-card swot-t"><h3>Threats</h3><ul><li>New competitors</li><li>Pricing pressure</li></ul></div>
    </div>
</div>

<div class="slide">
    <h2>Next Steps</h2>
    <ul>
        <li>Review Q1 targets</li>
        <li>Finalize hiring plan</li>
        <li>Ship v2.0 by end of quarter</li>
    </ul>
</div>

{SLIDE_NAV_CONTROLS}
{SLIDE_NAV_SCRIPT}
</body>
</html>
"""


_register("business", "Business review deck with KPI cards, charts, and SWOT analysis", _build_business)


# ─── Template: Tech (conference talk / technical documentation) ───


def _build_tech(title: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{SLIDE_BASE_CSS}
    pre {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem;
           font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 0.95rem;
           overflow-x: auto; width: 100%; max-width: 800px; text-align: left; }}
    code {{ color: #c9d1d9; }}
    .keyword {{ color: #ff7b72; }}
    .string {{ color: #a5d6ff; }}
    .comment {{ color: #8b949e; }}
    .function {{ color: #d2a8ff; }}
    .arch-diagram {{ display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; justify-content: center; }}
    .arch-box {{
        padding: 1rem 1.5rem; border-radius: 8px; text-align: center;
        font-weight: 600; min-width: 120px;
    }}
    .arch-frontend {{ background: #1f6feb33; border: 2px solid #1f6feb; color: #58a6ff; }}
    .arch-backend {{ background: #23863633; border: 2px solid #238636; color: #3fb950; }}
    .arch-data {{ background: #f0883e33; border: 2px solid #f0883e; color: #f0883e; }}
    .arch-arrow {{ color: #484f58; font-size: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 800px; }}
    th, td {{ border: 1px solid #30363d; padding: 0.8rem 1rem; text-align: left; }}
    th {{ background: #161b22; color: #58a6ff; }}
    tr:nth-child(even) {{ background: #161b2266; }}
    .badge {{ padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }}
    .badge-get {{ background: #23863633; color: #3fb950; }}
    .badge-post {{ background: #1f6feb33; color: #58a6ff; }}
</style>
</head>
<body>

<div class="slide" style="background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);">
    <h1>{title}</h1>
    <p>Technical Presentation</p>
</div>

<div class="slide">
    <h2>System Architecture</h2>
    <div class="arch-diagram">
        <div class="arch-box arch-frontend">Frontend<br><small>React + Vite</small></div>
        <span class="arch-arrow">→</span>
        <div class="arch-box arch-backend">API Gateway<br><small>FastAPI</small></div>
        <span class="arch-arrow">→</span>
        <div class="arch-box arch-backend">Auth Service<br><small>JWT</small></div>
        <span class="arch-arrow">→</span>
        <div class="arch-box arch-data">Database<br><small>PostgreSQL</small></div>
    </div>
</div>

<div class="slide">
    <h2>Code Example</h2>
<pre><code><span class="comment"># API endpoint example</span>
<span class="keyword">from</span> fastapi <span class="keyword">import</span> FastAPI

app = FastAPI()

<span class="keyword">@app</span>.get(<span class="string">"/api/users"</span>)
<span class="keyword">async def</span> <span class="function">get_users</span>():
    <span class="keyword">return</span> {{<span class="string">"users"</span>: [<span class="string">"alice"</span>, <span class="string">"bob"</span>]}}
</code></pre>
</div>

<div class="slide">
    <h2>API Reference</h2>
    <table>
        <tr><th>Method</th><th>Endpoint</th><th>Description</th><th>Auth</th></tr>
        <tr><td><span class="badge badge-get">GET</span></td><td>/api/users</td><td>List all users</td><td>Yes</td></tr>
        <tr><td><span class="badge badge-post">POST</span></td><td>/api/users</td><td>Create user</td><td>Yes</td></tr>
        <tr><td><span class="badge badge-get">GET</span></td><td>/api/health</td><td>Health check</td><td>No</td></tr>
    </table>
</div>

<div class="slide">
    <h2>Feature Comparison</h2>
    <table>
        <tr><th>Feature</th><th>Our Tool</th><th>Competitor A</th><th>Competitor B</th></tr>
        <tr><td>Real-time sync</td><td>✅</td><td>✅</td><td>❌</td></tr>
        <tr><td>Offline mode</td><td>✅</td><td>❌</td><td>✅</td></tr>
        <tr><td>API access</td><td>✅</td><td>✅</td><td>❌</td></tr>
        <tr><td>Self-hosted</td><td>✅</td><td>❌</td><td>❌</td></tr>
    </table>
</div>

<div class="slide">
    <h2>Key Takeaways</h2>
    <ul>
        <li>Architecture is modular and extensible</li>
        <li>API-first design enables integrations</li>
        <li>Open source and self-hostable</li>
    </ul>
</div>

{SLIDE_NAV_CONTROLS}
{SLIDE_NAV_SCRIPT}
</body>
</html>
"""


_register("tech", "Technical presentation with code blocks, architecture diagrams, and comparison tables", _build_tech)


# ─── Style Presets (adapted from zarazhangrui/frontend-slides STYLE_PRESETS.md, MIT) ───
#
# Each preset is a complete multi-slide deck in a specific aesthetic. Slide objects
# carry stable `data-oid` so the differ can produce stable selectors regardless of
# DOM-path drift after the user moves things around in the editor.

# Mandatory viewport-base CSS — shared by every preset. Adapted from frontend-slides
# viewport-base.css (MIT). This makes overflow physically impossible.
PRESET_VIEWPORT_BASE = """\
html, body { height: 100%; overflow-x: hidden; margin: 0; padding: 0; }
html { scroll-snap-type: y mandatory; scroll-behavior: smooth; }
*, *::before, *::after { box-sizing: border-box; }
.slide {
    width: 100vw; height: 100vh; height: 100dvh;
    overflow: hidden; scroll-snap-align: start;
    display: flex; flex-direction: column; position: relative;
}
:root {
    --title-size: clamp(1.5rem, 5vw, 4rem);
    --h2-size:    clamp(1.25rem, 3.5vw, 2.5rem);
    --h3-size:    clamp(1rem, 2.5vw, 1.75rem);
    --body-size:  clamp(0.75rem, 1.5vw, 1.125rem);
    --small-size: clamp(0.65rem, 1vw, 0.875rem);
    --slide-padding: clamp(1rem, 4vw, 4rem);
    --content-gap:   clamp(0.5rem, 2vw, 2rem);
}
@media (max-height: 700px) { :root { --slide-padding: clamp(0.75rem, 3vw, 2rem); --title-size: clamp(1.25rem, 4.5vw, 2.5rem); } }
@media (max-height: 600px) { :root { --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem); --title-size: clamp(1.1rem, 4vw, 2rem); --body-size: clamp(0.7rem, 1.2vw, 0.95rem); } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .2s !important; } }
"""

# Shared nav script — keyboard + click + counter, scoped to .slide elements.
PRESET_NAV_SCRIPT = """\
<script>
(function() {
    const slides = Array.from(document.querySelectorAll('section.slide'));
    const counter = document.getElementById('deck-counter');
    let i = 0;
    function show(n) {
        i = Math.max(0, Math.min(slides.length - 1, n));
        slides.forEach((s, k) => s.classList.toggle('is-active', k === i));
        if (counter) counter.textContent = (i + 1) + ' / ' + slides.length;
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); show(i + 1); }
        if (e.key === 'ArrowLeft')                   { e.preventDefault(); show(i - 1); }
        if (e.key === 'Home') show(0);
        if (e.key === 'End')  show(slides.length - 1);
    });
    document.querySelectorAll('[data-action="next"]').forEach(b => b.addEventListener('click', () => show(i + 1)));
    document.querySelectorAll('[data-action="prev"]').forEach(b => b.addEventListener('click', () => show(i - 1)));
    show(0);
})();
</script>
"""


# ─── Preset 1: Bold Signal (dark, high-impact, colored card focal point) ───


def _build_bold_signal(title: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{PRESET_VIEWPORT_BASE}
:root {{
    --bg: #1a1a1a;
    --bg-grad: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
    --card: #FF5722;
    --fg: #ffffff;
    --fg-on-card: #1a1a1a;
    --font-display: 'Archivo Black', sans-serif;
    --font-body: 'Space Grotesk', sans-serif;
}}
body {{ background: var(--bg); color: var(--fg); font-family: var(--font-body); }}
.slide {{ background: var(--bg-grad); padding: var(--slide-padding); display: none; }}
.slide.is-active {{ display: flex; }}
.slide-num {{ position: absolute; top: 4vh; left: 4vw; font-family: var(--font-display); font-size: clamp(1rem, 2vw, 1.5rem); opacity: .4; }}
.slide-nav {{ position: absolute; top: 4vh; right: 4vw; display: flex; gap: 1.5rem; font-size: var(--small-size); letter-spacing: .1em; text-transform: uppercase; }}
.slide-nav span {{ opacity: .4; }}
.slide-nav span.active {{ opacity: 1; }}
.card {{
    background: var(--card); color: var(--fg-on-card);
    border-radius: 24px;
    padding: clamp(2rem, 5vw, 4rem);
    margin: auto 0 6vh;
    max-width: min(90vw, 900px);
}}
h1 {{ font-family: var(--font-display); font-size: var(--title-size); line-height: .95; margin-bottom: var(--content-gap); }}
h2 {{ font-family: var(--font-display); font-size: var(--h2-size); line-height: 1; }}
.lede {{ font-size: var(--body-size); max-width: 60ch; opacity: .9; margin-top: 1rem; }}
#deck-counter {{ position: fixed; bottom: 2vh; left: 50%; transform: translateX(-50%); font-size: var(--small-size); opacity: .5; z-index: 10; }}
.nav-btns {{ position: fixed; bottom: 2vh; right: 2vw; display: flex; gap: .5rem; z-index: 10; }}
.nav-btns button {{ background: transparent; border: 1px solid #666; color: var(--fg); width: 36px; height: 36px; border-radius: 50%; cursor: pointer; }}
</style>
</head>
<body>

<section class="slide is-active" id="slide-1" data-oid="s1">
  <div class="slide-num">01 / 04</div>
  <div class="slide-nav"><span class="active">Intro</span><span>Vision</span><span>Plan</span><span>Ask</span></div>
  <div class="card" data-oid="s1-card">
    <h1 data-oid="s1-title">{title}</h1>
    <p class="lede" data-oid="s1-lede">A bold statement that sets the tone. Replace this with the one sentence your audience must remember.</p>
  </div>
</section>

<section class="slide" id="slide-2" data-oid="s2">
  <div class="slide-num">02 / 04</div>
  <div class="slide-nav"><span>Intro</span><span class="active">Vision</span><span>Plan</span><span>Ask</span></div>
  <div class="card" data-oid="s2-card">
    <h2 data-oid="s2-title">The world we're building toward.</h2>
    <p class="lede" data-oid="s2-lede">Describe the desired end state in one paragraph. Keep it visual, concrete, and free of jargon.</p>
  </div>
</section>

<section class="slide" id="slide-3" data-oid="s3">
  <div class="slide-num">03 / 04</div>
  <div class="slide-nav"><span>Intro</span><span>Vision</span><span class="active">Plan</span><span>Ask</span></div>
  <div class="card" data-oid="s3-card">
    <h2 data-oid="s3-title">How we get there.</h2>
    <p class="lede" data-oid="s3-lede">Three to five concrete steps. Numbers, dates, owners. No vague verbs.</p>
  </div>
</section>

<section class="slide" id="slide-4" data-oid="s4">
  <div class="slide-num">04 / 04</div>
  <div class="slide-nav"><span>Intro</span><span>Vision</span><span>Plan</span><span class="active">Ask</span></div>
  <div class="card" data-oid="s4-card">
    <h2 data-oid="s4-title">What we need from you.</h2>
    <p class="lede" data-oid="s4-lede">A single, unambiguous ask. Make it impossible to leave the room without a decision.</p>
  </div>
</section>

<span id="deck-counter">1 / 4</span>
<div class="nav-btns">
  <button data-action="prev" aria-label="Previous">←</button>
  <button data-action="next" aria-label="Next">→</button>
</div>
{PRESET_NAV_SCRIPT}
</body>
</html>
"""


_register_preset("bold-signal", "Dark gradient + bold orange focal card. High-impact pitch / launch deck.", _build_bold_signal)


# ─── Preset 2: Dark Botanical (elegant, premium, abstract gradient circles) ───


def _build_dark_botanical(title: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@300;400&display=swap" rel="stylesheet">
<style>
{PRESET_VIEWPORT_BASE}
:root {{
    --bg: #0f0f0f;
    --fg: #e8e4df;
    --fg-muted: #9a9590;
    --accent-warm: #d4a574;
    --accent-pink: #e8b4b8;
    --accent-gold: #c9b896;
    --font-display: 'Cormorant', serif;
    --font-body: 'IBM Plex Sans', sans-serif;
}}
body {{ background: var(--bg); color: var(--fg); font-family: var(--font-body); font-weight: 300; }}
.slide {{ padding: var(--slide-padding); display: none; align-items: center; justify-content: center; text-align: center; }}
.slide.is-active {{ display: flex; }}
/* Abstract soft gradient circles in corner */
.slide::before, .slide::after {{
    content: ""; position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none;
}}
.slide::before {{ width: 40vw; height: 40vw; background: var(--accent-warm); opacity: .12; top: -10vw; right: -10vw; }}
.slide::after  {{ width: 30vw; height: 30vw; background: var(--accent-pink); opacity: .08; bottom: -8vw; left: -8vw; }}
.accent-line {{ width: 1px; height: clamp(2rem, 6vh, 4rem); background: var(--accent-gold); margin: 0 auto var(--content-gap); }}
.eyebrow {{ font-size: var(--small-size); letter-spacing: .3em; text-transform: uppercase; color: var(--accent-gold); margin-bottom: 1rem; }}
h1 {{ font-family: var(--font-display); font-weight: 400; font-size: var(--title-size); line-height: 1.05; max-width: 18ch; margin: 0 auto; }}
h2 {{ font-family: var(--font-display); font-weight: 400; font-size: var(--h2-size); line-height: 1.1; max-width: 22ch; margin: 0 auto; }}
.lede {{ font-size: var(--body-size); max-width: 50ch; margin: var(--content-gap) auto 0; color: var(--fg-muted); line-height: 1.7; }}
.signature {{ font-family: var(--font-display); font-style: italic; font-size: var(--body-size); color: var(--accent-warm); margin-top: var(--content-gap); }}
.content {{ position: relative; z-index: 1; }}
#deck-counter {{ position: fixed; bottom: 2vh; left: 50%; transform: translateX(-50%); font-size: var(--small-size); color: var(--fg-muted); letter-spacing: .2em; z-index: 10; }}
.nav-btns {{ position: fixed; bottom: 2vh; right: 2vw; display: flex; gap: .5rem; z-index: 10; }}
.nav-btns button {{ background: transparent; border: 1px solid var(--fg-muted); color: var(--fg); width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-family: var(--font-display); }}
</style>
</head>
<body>

<section class="slide is-active" id="slide-1" data-oid="s1">
  <div class="content">
    <div class="eyebrow" data-oid="s1-eyebrow">Chapter One</div>
    <div class="accent-line"></div>
    <h1 data-oid="s1-title">{title}</h1>
    <p class="signature" data-oid="s1-sig">— a quiet introduction</p>
  </div>
</section>

<section class="slide" id="slide-2" data-oid="s2">
  <div class="content">
    <div class="eyebrow" data-oid="s2-eyebrow">The premise</div>
    <h2 data-oid="s2-title">Beauty is the discipline of removing everything that does not belong.</h2>
    <p class="lede" data-oid="s2-lede">Replace this with the single thought that justifies the entire deck. One paragraph, no bullets.</p>
  </div>
</section>

<section class="slide" id="slide-3" data-oid="s3">
  <div class="content">
    <div class="eyebrow" data-oid="s3-eyebrow">The proof</div>
    <h2 data-oid="s3-title">Three observations that changed how we think.</h2>
    <p class="lede" data-oid="s3-lede">Briefly enumerate the three findings — but in prose, not bullets. The list lives in the reader's head, not on the slide.</p>
  </div>
</section>

<section class="slide" id="slide-4" data-oid="s4">
  <div class="content">
    <div class="eyebrow" data-oid="s4-eyebrow">The invitation</div>
    <h2 data-oid="s4-title">What we'd like to do together.</h2>
    <p class="signature" data-oid="s4-sig">— with care</p>
  </div>
</section>

<span id="deck-counter">1 / 4</span>
<div class="nav-btns">
  <button data-action="prev" aria-label="Previous">‹</button>
  <button data-action="next" aria-label="Next">›</button>
</div>
{PRESET_NAV_SCRIPT}
</body>
</html>
"""


_register_preset("dark-botanical", "Elegant serif on dark with soft gradient circles. For premium / investor / luxury decks.", _build_dark_botanical)


# ─── Preset 3: Terminal Green (developer / hacker aesthetic) ───


def _build_terminal_green(title: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
{PRESET_VIEWPORT_BASE}
:root {{
    --bg: #0d1117;
    --fg: #c9d1d9;
    --green: #39d353;
    --green-dim: #1f7a30;
    --comment: #6e7681;
    --font: 'JetBrains Mono', monospace;
}}
body {{ background: var(--bg); color: var(--fg); font-family: var(--font); font-size: var(--body-size); }}
/* subtle scan lines */
body::before {{
    content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 100;
    background: repeating-linear-gradient(180deg, transparent 0, transparent 3px, rgba(0,0,0,.06) 3px, rgba(0,0,0,.06) 4px);
}}
.slide {{ padding: var(--slide-padding); display: none; flex-direction: column; justify-content: center; }}
.slide.is-active {{ display: flex; }}
.prompt {{ color: var(--green); margin-bottom: 1rem; font-size: var(--small-size); opacity: .8; }}
.prompt::before {{ content: "$ "; color: var(--green-dim); }}
h1 {{ font-family: var(--font); font-weight: 700; color: var(--green); font-size: var(--title-size); line-height: 1.15; max-width: 24ch; }}
h2 {{ font-family: var(--font); font-weight: 700; color: var(--green); font-size: var(--h2-size); line-height: 1.2; }}
.cursor {{ display: inline-block; width: .6em; height: 1em; background: var(--green); vertical-align: text-bottom; animation: blink 1.1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.comment {{ color: var(--comment); margin-bottom: 1rem; }}
.comment::before {{ content: "// "; }}
ul {{ list-style: none; padding: 0; margin: var(--content-gap) 0 0; max-width: 70ch; }}
ul li {{ padding: .35rem 0; }}
ul li::before {{ content: "→ "; color: var(--green); }}
pre {{
    background: #161b22; border: 1px solid #30363d; border-radius: 6px;
    padding: 1.2rem 1.5rem; max-width: min(90vw, 900px); font-size: var(--small-size);
    overflow: auto; margin-top: var(--content-gap);
}}
.kw {{ color: #ff7b72; }}
.str {{ color: #a5d6ff; }}
.fn {{ color: #d2a8ff; }}
#deck-counter {{ position: fixed; bottom: 2vh; left: 2vw; color: var(--green-dim); font-size: var(--small-size); z-index: 10; }}
.nav-btns {{ position: fixed; bottom: 2vh; right: 2vw; display: flex; gap: .5rem; z-index: 10; }}
.nav-btns button {{ background: transparent; border: 1px solid var(--green-dim); color: var(--green); width: 36px; height: 36px; cursor: pointer; font-family: var(--font); }}
.nav-btns button:hover {{ background: var(--green-dim); color: var(--bg); }}
</style>
</head>
<body>

<section class="slide is-active" id="slide-1" data-oid="s1">
  <div class="prompt" data-oid="s1-prompt">cat README.md</div>
  <h1 data-oid="s1-title">{title}<span class="cursor"></span></h1>
  <p class="comment" data-oid="s1-comment">a developer-first introduction</p>
</section>

<section class="slide" id="slide-2" data-oid="s2">
  <div class="prompt" data-oid="s2-prompt">./why.sh</div>
  <h2 data-oid="s2-title">why this exists</h2>
  <ul data-oid="s2-list">
    <li>The status quo wastes everyone's time</li>
    <li>Existing tools optimize for the wrong axis</li>
    <li>We have a better way; here it is</li>
  </ul>
</section>

<section class="slide" id="slide-3" data-oid="s3">
  <div class="prompt" data-oid="s3-prompt">demo.py</div>
  <h2 data-oid="s3-title">how it works</h2>
<pre data-oid="s3-code"><code><span class="kw">from</span> tool <span class="kw">import</span> Pipeline

pipe = Pipeline(<span class="str">"input.json"</span>)
result = pipe.<span class="fn">run</span>()
<span class="kw">print</span>(result.summary)
</code></pre>
</section>

<section class="slide" id="slide-4" data-oid="s4">
  <div class="prompt" data-oid="s4-prompt">git push origin main</div>
  <h2 data-oid="s4-title">what's next</h2>
  <ul data-oid="s4-list">
    <li>Open source on GitHub today</li>
    <li>v1.0 ships next month</li>
    <li>Contributors welcome — see CONTRIBUTING.md</li>
  </ul>
</section>

<span id="deck-counter">[1/4]</span>
<div class="nav-btns">
  <button data-action="prev" aria-label="Previous">[</button>
  <button data-action="next" aria-label="Next">]</button>
</div>
{PRESET_NAV_SCRIPT}
</body>
</html>
"""


_register_preset("terminal-green", "Mono + scan lines + GitHub-dark green. For DevTools / infra / open-source decks.", _build_terminal_green)
