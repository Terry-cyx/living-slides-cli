"""Presentation templates for htmlcli — real-world PPT replacement scenarios."""

from __future__ import annotations

TEMPLATES: dict[str, dict] = {}


def _register(name: str, description: str, builder):
    TEMPLATES[name] = {"description": description, "builder": builder}


def get_template(name: str, title: str) -> str:
    if name not in TEMPLATES:
        raise ValueError(f"Unknown template: {name}. Available: {', '.join(TEMPLATES)}")
    return TEMPLATES[name]["builder"](title)


def list_templates() -> list[dict]:
    return [{"name": k, "description": v["description"]} for k, v in TEMPLATES.items()]


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
