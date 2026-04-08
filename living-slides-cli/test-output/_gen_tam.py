import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from htmlcli.assets import save_external_image
import tempfile, os

bg = "#0A0A0A"
fg = "#FAFAFA"
muted = "#A1A1AA"
primary = "#8B5CF6"
accent = "#F43F5E"

fig, ax = plt.subplots(figsize=(12, 7.2), facecolor=bg)
ax.set_facecolor(bg)
ax.set_xlim(-6, 10)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')
ax.axis('off')

# Concentric circles - radius proportional to sqrt(value) for area perception
import math
tam_v, sam_v, som_v = 520, 80, 3
def r(v): return math.sqrt(v) * 0.18
r_tam, r_sam, r_som = r(tam_v), r(sam_v), r(som_v)

cx, cy = -1, 0
ax.add_patch(mpatches.Circle((cx, cy), r_tam, facecolor=primary, alpha=0.18, edgecolor=primary, linewidth=2))
ax.add_patch(mpatches.Circle((cx, cy), r_sam, facecolor=primary, alpha=0.32, edgecolor=primary, linewidth=2))
ax.add_patch(mpatches.Circle((cx, cy), r_som, facecolor=accent, alpha=0.85, edgecolor=accent, linewidth=2))

# Labels with leader lines
def label(x, y, lx, ly, title, val, sub):
    ax.plot([x, lx-0.1], [y, ly], color=muted, linewidth=0.8)
    ax.text(lx, ly+0.35, title, color=muted, fontsize=12, fontweight='bold', va='center')
    ax.text(lx, ly-0.05, val, color=fg, fontsize=22, fontweight='bold', va='center')
    ax.text(lx, ly-0.55, sub, color=muted, fontsize=10, va='center')

label(cx + r_tam*0.7, cy + r_tam*0.7, 5.0, 3.0, "TAM", "$520B", "Global Enterprise AI Software")
label(cx + r_sam*0.7, cy + r_sam*0.7, 5.0, 0.8, "SAM", "$80B", "Mid-to-Large Enterprise AI Platform")
label(cx, cy - r_som - 0.1, 5.0, -1.4, "SOM", "$3B", "3-Year Reachable Share")

plt.tight_layout()
tmp = os.path.join(tempfile.gettempdir(), "tam_circles.png")
plt.savefig(tmp, facecolor=bg, dpi=120, bbox_inches='tight')
plt.close()

rel = save_external_image("test-output/test04.html", "tam-circles", tmp)
print(rel)
