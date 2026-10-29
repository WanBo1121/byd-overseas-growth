"""BYD overseas growth decomposition. Run: python analysis.py"""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for f in fm.findSystemFonts():
    if "NotoSansCJK" in f:
        fm.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK SC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("data/annual.csv").set_index("year")
df["domestic"] = df.total_sales - df.overseas_sales
df["overseas_share"] = df.overseas_sales / df.total_sales

rows = []
for y in df.index[1:]:
    p, c = df.loc[y-1], df.loc[y]
    base = p.total_sales
    rows.append(dict(
        period=f"{y-1}→{y}",
        total_growth_pct=(c.total_sales - base) / base * 100,
        overseas_contrib_pp=(c.overseas_sales - p.overseas_sales) / base * 100,
        domestic_contrib_pp=(c.domestic - p.domestic) / base * 100,
        overseas_yoy_pct=(c.overseas_sales / p.overseas_sales - 1) * 100,
        domestic_yoy_pct=(c.domestic / p.domestic - 1) * 100))
res = pd.DataFrame(rows).round(2)
assert ((res.overseas_contrib_pp + res.domestic_contrib_pp - res.total_growth_pct).abs() < 0.02).all()
res.to_csv("data/results.csv", index=False)
print(df[["total_sales", "overseas_sales", "domestic", "overseas_share"]].round(4))
print(res.to_string(index=False))

INK, BLUE, RED, GREY = "#222", "#2b6cb0", "#c0392b", "#8a8f98"

# Chart 1: overseas share trend
fig, ax = plt.subplots(figsize=(7, 4.2))
labels = [str(y) for y in df.index] + ["2026\n1-9月"]
shares = list(df.overseas_share * 100) + [42.7]
cols = [BLUE] * 3 + [GREY]
b = ax.bar(labels, shares, color=cols, width=.55)
for r, v in zip(b, shares):
    ax.text(r.get_x() + r.get_width()/2, v + .8, f"{v:.1f}%", ha="center", color=INK)
ax.set_ylabel("海外销量占总销量比例 (%)"); ax.set_ylim(0, 52)
ax.set_title("比亚迪:海外销量占比从 8% 升至 43%", loc="left", color=INK)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.text(.01, .01, "2026年1-9月占比为媒体引述值(来源S7);口径:海外销量/总销量,见README局限性", fontsize=7, color=GREY)
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig("charts/01_overseas_share.png", dpi=200); plt.close()

# Chart 2: waterfall of growth contribution (pp)
fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
axes[0].set_ylim(-14, 47)
for ax, (_, r) in zip(axes, res.iterrows()):
    o, d, t = r.overseas_contrib_pp, r.domestic_contrib_pp, r.total_growth_pct
    start = 0
    parts = [("国内", d, d), ("海外", o, o)]
    x = 0
    for name, val, _ in parts:
        ax.bar(name, val, bottom=start, color=BLUE if val >= 0 else RED, width=.55)
        ax.text(name, (start + val + 1.0) if val >= 0 else (start + val - 1.0), f"{val:+.1f}pp", ha="center", va="bottom" if val >= 0 else "top", color=INK)
        start += val
    ax.bar("总增速", t, color=GREY, width=.55)
    ax.text("总增速", t + 1.0, f"{t:+.1f}%", ha="center", color=INK)
    ax.axhline(0, color=INK, lw=.6)
    ax.set_title(r.period, color=INK)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axes[0].set_ylabel("对总销量增速的贡献 (百分点)")
fig.suptitle("比亚迪销量增长拆解:2025年增长全部来自海外,国内为负贡献", x=.01, ha="left", color=INK)
fig.text(.01, .01, "贡献(pp) = 该部分销量变化 / 上年总销量;海外为四舍五入值,国内=总销量−海外(口径差异见README)", fontsize=7, color=GREY)
fig.tight_layout(rect=(0, .03, 1, .95)); fig.savefig("charts/02_growth_contribution.png", dpi=200); plt.close()
