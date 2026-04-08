"""Generate all matplotlib charts for test09 product roadmap deck."""
import sys
from pathlib import Path

# Ensure we can import htmlcli
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from htmlcli.assets import generate_chart, get_assets_dir

HTML = str(Path(__file__).parent / "test09.html")

# Theme
BG = "#0A0A0A"
FG = "#FAFAFA"
MUTED = "#A1A1AA"
GRID = "#27272A"
PRIMARY = "#6366F1"
ACCENT = "#F59E0B"
SUCCESS = "#10B981"
ERROR = "#EF4444"
INFO = "#3B82F6"
PINK = "#EC4899"

PALETTE = [PRIMARY, PINK, ACCENT, SUCCESS, INFO, "#8B5CF6", "#14B8A6"]

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "axes.edgecolor": GRID,
    "axes.labelcolor": FG,
    "axes.titlecolor": FG,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": FG,
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "Noto Sans SC", "SimHei", "Inter", "Arial", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.color": GRID,
    "grid.alpha": 0.3,
})

ASSETS = get_assets_dir(HTML)


def save(fig, name):
    out = ASSETS / f"{name}.png"
    fig.savefig(out, facecolor=BG, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {out}")


# ---------- Round 0: initial gantt timeline ----------
def gantt_initial():
    """Initial gantt chart with original Q2 dates."""
    tasks = [
        ("Platform 升级",        0,  10, PRIMARY),
        ("移动端 v3.0",          2,  12, PINK),
        ("数据中台",              8,  16, ACCENT),
        ("企业版 SSO",            10, 14, SUCCESS),
        ("国际化 i18n",           14, 22, INFO),
        ("AI 助手 Beta",          18, 28, "#8B5CF6"),
        ("性能优化",              24, 32, "#14B8A6"),
        ("开放 API v2",           30, 40, PRIMARY),
        ("合规 SOC2",             34, 44, ACCENT),
        ("年度发布",              44, 52, ERROR),
    ]
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=120)
    for i, (name, start, end, color) in enumerate(tasks):
        ax.broken_barh([(start, end - start)], (i - 0.35, 0.7),
                       facecolors=color, edgecolor="none")
        ax.text(end + 0.4, i, f"W{start}-W{end}", va="center",
                color=MUTED, fontsize=9)
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([t[0] for t in tasks])
    ax.invert_yaxis()
    ax.set_xlim(0, 56)
    ax.set_xticks([0, 13, 26, 39, 52])
    ax.set_xticklabels(["W1", "Q2 起", "Q3 起", "Q4 起", "Y末"])
    # Quarter dividers
    for w in [13, 26, 39]:
        ax.axvline(w, color=GRID, linestyle="--", linewidth=1)
    ax.set_title("2026 产品路线图 Gantt（初版）", fontsize=15, fontweight="bold", pad=14)
    ax.grid(True, axis="x")
    plt.tight_layout()
    save(fig, "gantt-initial")


# ---------- Round 1: updated gantt (Q2 pushed 2 weeks later) ----------
def gantt_updated():
    """Q2 milestones pushed 2 weeks later. Q2 = weeks 13-26."""
    def shift(start, end):
        # Shift any task that starts in Q2 (weeks 13-26) by +2 weeks
        if 13 <= start <= 26:
            return start + 2, end + 2
        return start, end
    base = [
        ("Platform 升级",        0,  10, PRIMARY),
        ("移动端 v3.0",          2,  12, PINK),
        ("数据中台",              8,  16, ACCENT),
        ("企业版 SSO",            10, 14, SUCCESS),
        ("国际化 i18n",           14, 22, INFO),       # Q2 -> +2
        ("AI 助手 Beta",          18, 28, "#8B5CF6"),  # Q2 -> +2
        ("性能优化",              24, 32, "#14B8A6"),  # Q2 -> +2
        ("开放 API v2",           30, 40, PRIMARY),
        ("合规 SOC2",             34, 44, ACCENT),
        ("年度发布",              44, 52, ERROR),
    ]
    tasks = [(n, *shift(s, e), c) for n, s, e, c in base]
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=120)
    for i, (name, start, end, color) in enumerate(tasks):
        ax.broken_barh([(start, end - start)], (i - 0.35, 0.7),
                       facecolors=color, edgecolor="none")
        # Highlight shifted bars
        if 15 <= start <= 28:
            ax.text(end + 0.4, i, f"W{start}-W{end}  +2w", va="center",
                    color=ACCENT, fontsize=9, fontweight="bold")
        else:
            ax.text(end + 0.4, i, f"W{start}-W{end}", va="center",
                    color=MUTED, fontsize=9)
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([t[0] for t in tasks])
    ax.invert_yaxis()
    ax.set_xlim(0, 58)
    ax.set_xticks([0, 13, 26, 39, 52])
    ax.set_xticklabels(["W1", "Q2 起", "Q3 起", "Q4 起", "Y末"])
    for w in [13, 26, 39]:
        ax.axvline(w, color=GRID, linestyle="--", linewidth=1)
    ax.set_title("2026 路线图 Gantt（Q2 顺延 2 周）", fontsize=15, fontweight="bold", pad=14)
    ax.grid(True, axis="x")
    plt.tight_layout()
    save(fig, "gantt-updated")


# ---------- Resource distribution (initial bar) ----------
def resource_bar():
    teams = ["Platform", "Mobile", "Data", "AI", "Infra", "Design", "QA"]
    headcount = [12, 9, 8, 7, 5, 4, 6]
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=120)
    bars = ax.bar(teams, headcount, color=PALETTE[:len(teams)])
    for b, v in zip(bars, headcount):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, str(v),
                ha="center", color=FG, fontweight="bold")
    ax.set_ylabel("Headcount")
    ax.set_ylim(0, max(headcount) + 3)
    ax.set_title("2026 资源分配（按团队）", fontsize=14, fontweight="bold", pad=12)
    ax.grid(True, axis="y")
    plt.tight_layout()
    save(fig, "resource-bar")


# ---------- Round 2: priority matrix (impact vs cost) ----------
def priority_matrix():
    features = [
        ("Platform 升级",   4.0, 8.5, PRIMARY),
        ("移动端 v3.0",     5.0, 7.0, PINK),
        ("数据中台",         7.5, 9.0, ACCENT),
        ("企业版 SSO",       3.0, 6.5, SUCCESS),
        ("国际化 i18n",      4.5, 5.5, INFO),
        ("AI 助手 Beta",     6.5, 8.0, "#8B5CF6"),
        ("性能优化",         3.5, 7.5, "#14B8A6"),
        ("开放 API v2",      5.5, 7.8, PRIMARY),
        ("合规 SOC2",        6.0, 6.5, ACCENT),
        ("AI 智能推荐 ★",    4.0, 9.5, ERROR),  # New feature, highlighted
    ]
    fig, ax = plt.subplots(figsize=(10.5, 7), dpi=120)
    for name, cost, impact, color in features:
        is_new = "★" in name
        ax.scatter(cost, impact,
                   s=320 if is_new else 200,
                   c=color,
                   edgecolors=FG if is_new else "none",
                   linewidths=2 if is_new else 0,
                   alpha=0.95 if is_new else 0.85,
                   zorder=3)
        ax.annotate(name, (cost, impact),
                    xytext=(8, 6), textcoords="offset points",
                    color=FG if is_new else MUTED,
                    fontsize=10 if is_new else 9,
                    fontweight="bold" if is_new else "normal")
    # Quadrant lines
    ax.axhline(7, color=GRID, linestyle="--", linewidth=1)
    ax.axvline(5, color=GRID, linestyle="--", linewidth=1)
    # Quadrant labels
    ax.text(1.5, 9.6, "快赢区\n(低成本·高影响)", color=SUCCESS, fontsize=10, ha="center")
    ax.text(8.5, 9.6, "战略投入\n(高成本·高影响)", color=ACCENT, fontsize=10, ha="center")
    ax.text(1.5, 4.6, "填空区\n(低成本·低影响)", color=MUTED, fontsize=10, ha="center")
    ax.text(8.5, 4.6, "重新评估\n(高成本·低影响)", color=ERROR, fontsize=10, ha="center")
    ax.set_xlim(0, 10)
    ax.set_ylim(4, 10.3)
    ax.set_xlabel("成本 Cost →", fontsize=12)
    ax.set_ylabel("影响 Impact →", fontsize=12)
    ax.set_title("功能优先级矩阵：影响 vs 成本", fontsize=14, fontweight="bold", pad=14)
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    save(fig, "priority-matrix")


# ---------- Round 3: resource allocation pie + grouped bar ----------
def resource_pie():
    teams = ["Platform", "Mobile", "Data/AI", "Infra", "Design", "QA"]
    values = [25, 18, 24, 12, 9, 12]
    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=120)
    wedges, texts, autotexts = ax.pie(
        values, labels=teams, colors=PALETTE[:len(teams)],
        autopct="%1.0f%%", startangle=90,
        pctdistance=0.78,
        textprops={"color": FG, "fontsize": 11},
        wedgeprops={"edgecolor": BG, "linewidth": 2},
    )
    for at in autotexts:
        at.set_color(FG)
        at.set_fontweight("bold")
    ax.set_title("2026 全年资源分配（团队占比）", fontsize=14, fontweight="bold", pad=14)
    ax.axis("equal")
    plt.tight_layout()
    save(fig, "resource-pie")


def resource_grouped():
    teams = ["Platform", "Mobile", "Data/AI", "Infra", "Design", "QA"]
    q1 = [28, 20, 18, 14, 8, 12]
    q2 = [24, 22, 22, 12, 8, 12]
    q3 = [22, 16, 28, 12, 10, 12]
    q4 = [20, 14, 30, 10, 12, 14]
    x = np.arange(len(teams))
    w = 0.2
    fig, ax = plt.subplots(figsize=(11, 5.8), dpi=120)
    ax.bar(x - 1.5*w, q1, w, label="Q1", color=PRIMARY)
    ax.bar(x - 0.5*w, q2, w, label="Q2", color=PINK)
    ax.bar(x + 0.5*w, q3, w, label="Q3", color=ACCENT)
    ax.bar(x + 1.5*w, q4, w, label="Q4", color=SUCCESS)
    ax.set_xticks(x)
    ax.set_xticklabels(teams)
    ax.set_ylabel("投入比例 %")
    ax.legend(loc="upper right", frameon=False)
    ax.set_title("各团队 Q1–Q4 投入分布", fontsize=14, fontweight="bold", pad=12)
    ax.grid(True, axis="y")
    plt.tight_layout()
    save(fig, "resource-grouped")


if __name__ == "__main__":
    gantt_initial()
    gantt_updated()
    resource_bar()
    priority_matrix()
    resource_pie()
    resource_grouped()
    print("All charts generated.")
