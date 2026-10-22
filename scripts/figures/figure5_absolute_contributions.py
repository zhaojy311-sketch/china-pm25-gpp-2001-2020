from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
UTILS_DIR = Path(__file__).resolve().parents[1] / "utils"
if str(UTILS_DIR) not in sys.path:
    sys.path.insert(0, str(UTILS_DIR))
from audit_panel_alignment import require_matplotlib_panel_alignment
from matplotlib import font_manager
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, StrMethodFormatter


ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "data" / "review_required" / "figure5" / "Figure5_absolute_contributions.xlsx"
OUTPUT_DIR = ROOT / "outputs" / "figure5"

FONT_SIZE = 16
REGION_LABEL_SIZE = 18
DPI = 300
AXIS_COLOR = "#000000"
AXIS_LINEWIDTH = 1.2
TICK_LENGTH = 4.0
CONNECTOR_COLOR = "#D5D5D5"
GPP_COLOR = "#A0A0A4"  # 与参考图中的 GPP 灰色一致。

# 与“八大区域年增长率折线图”完全一致的因子颜色。
FACTOR_COLORS = {
    "LAI": "#2457A6",
    "PAR": "#CB0505",
    "PM2.5": "#8B2DB2",
    "Pre": "#FF7F00",
    "RH": "#00BFC4",
    "Ta": "#FFC400",
    "VPD": "#A0522D",
    "NTL": "#62F000",
}

REGION_GRID = [["FW", "NE"], ["NW", "NC"], ["SWC", "EC"], ["CSC", "SC"]]

# 每个面板统一显示 5 个纵轴刻度；范围和间隔取整，避免拼图中标签过密。
Y_AXIS_SETTINGS = {
    "FW": (600, 1600, 250),
    "NE": (900, 1300, 100),
    "NW": (300, 600, 75),
    "NC": (450, 750, 75),
    "SWC": (800, 1200, 100),
    "EC": (1200, 2000, 200),
    "CSC": (1000, 2000, 250),
    "SC": (1500, 3100, 400),
}


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial"],
        "font.size": FONT_SIZE,
        "text.color": "#000000",
        "axes.edgecolor": "#000000",
        "axes.labelcolor": "#000000",
        "xtick.color": "#000000",
        "ytick.color": "#000000",
        "axes.labelsize": FONT_SIZE,
        "xtick.labelsize": FONT_SIZE,
        "ytick.labelsize": FONT_SIZE,
        "legend.fontsize": FONT_SIZE,
        "axes.unicode_minus": False,
        "mathtext.fontset": "custom",
        "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
)


@dataclass(frozen=True)
class WaterfallItem:
    kind: str
    label: str
    value: float


def display_number(value: float) -> str:
    if np.isclose(value, round(value)):
        return f"{int(round(value))}"
    return f"{value:.1f}".rstrip("0").rstrip(".")


def load_region_items(region: str) -> list[WaterfallItem]:
    workbook = openpyxl.load_workbook(INPUT_FILE, data_only=True, read_only=True)
    try:
        sheet = workbook[region]
        rows = [(row[0], row[1]) for row in sheet.iter_rows(values_only=True) if row[0] is not None]
    finally:
        workbook.close()

    items: list[WaterfallItem] = []
    seen_years: list[int] = []
    for label, value in rows:
        if not isinstance(value, (int, float)):
            raise ValueError(f"{region}: 非数值数据 {label!r}={value!r}")
        if isinstance(label, (int, float)):
            year = int(label)
            if year not in {2001, 2013, 2020}:
                raise ValueError(f"{region}: 无法识别年份 {label!r}")
            seen_years.append(year)
            items.append(WaterfallItem("total", str(year), float(value)))
        else:
            name = str(label).strip()
            if name not in FACTOR_COLORS:
                raise ValueError(f"{region}: 未配置因子颜色 {name!r}")
            items.append(WaterfallItem("factor", name, float(value)))

    if seen_years != [2001, 2013, 2020]:
        raise ValueError(f"{region}: 年份顺序应为 2001、2013、2020，实际为 {seen_years}")
    return items


def reconciliation_report(region: str, items: list[WaterfallItem]) -> list[str]:
    messages: list[str] = []
    current_total: float | None = None
    contribution_sum = 0.0
    start_year: str | None = None
    for item in items:
        if item.kind == "total":
            if current_total is not None and start_year is not None:
                difference = current_total + contribution_sum - item.value
                messages.append(
                    f"{region} {start_year}–{item.label}: "
                    f"起点+贡献-终点={difference:+.1f}"
                )
            current_total = item.value
            contribution_sum = 0.0
            start_year = item.label
        else:
            contribution_sum += item.value
    return messages


def style_axis(ax: plt.Axes, region: str, bottom_row: bool) -> None:
    ymin, ymax, step = Y_AXIS_SETTINGS[region]
    ax.set_ylim(ymin, ymax)
    ax.yaxis.set_major_locator(FixedLocator(np.arange(ymin, ymax + 0.5 * step, step)))
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))
    ax.set_ylabel(r"GPP-gC/(m$^2$·yr)", labelpad=8)
    ax.grid(False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for name in ("left", "bottom"):
        ax.spines[name].set_color(AXIS_COLOR)
        ax.spines[name].set_linewidth(AXIS_LINEWIDTH)

    ax.tick_params(
        axis="y",
        which="major",
        direction="out",
        length=TICK_LENGTH,
        width=AXIS_LINEWIDTH,
        color=AXIS_COLOR,
        labelcolor=AXIS_COLOR,
        pad=3,
    )
    ax.tick_params(
        axis="x",
        which="major",
        direction="out",
        length=TICK_LENGTH if bottom_row else 0,
        width=AXIS_LINEWIDTH,
        color=AXIS_COLOR,
        labelcolor=AXIS_COLOR,
        pad=4,
    )


def draw_waterfall(ax: plt.Axes, region: str, items: list[WaterfallItem], bottom_row: bool) -> None:
    x_positions = np.arange(len(items), dtype=float)
    bar_width = 0.86
    levels_after: list[float] = []
    current = 0.0
    total_positions: list[int] = []
    total_labels: list[str] = []

    for index, item in enumerate(items):
        if item.kind == "total":
            bottom = 0.0
            height = item.value
            color = GPP_COLOR
            current = item.value
            total_positions.append(index)
            total_labels.append(item.label)
            label_y = item.value
            label_offset = 3
            va = "bottom"
        else:
            next_level = current + item.value
            bottom = min(current, next_level)
            height = abs(item.value)
            color = FACTOR_COLORS[item.label]
            current = next_level
            if item.value >= 0:
                label_y = next_level
                label_offset = 3
                va = "bottom"
            else:
                label_y = next_level
                label_offset = -3
                va = "top"

        ax.bar(
            x_positions[index],
            height,
            width=bar_width,
            bottom=bottom,
            color=color,
            edgecolor="none",
            linewidth=0,
            zorder=3,
        )
        ax.annotate(
            display_number(item.value),
            xy=(x_positions[index], label_y),
            xytext=(0, label_offset),
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=FONT_SIZE,
            color="black",
            clip_on=False,
            zorder=5,
        )
        levels_after.append(current)

    for index in range(len(items) - 1):
        ax.plot(
            [x_positions[index] + bar_width / 2, x_positions[index + 1] - bar_width / 2],
            [levels_after[index], levels_after[index]],
            color=CONNECTOR_COLOR,
            linewidth=0.7,
            solid_capstyle="butt",
            zorder=2,
        )

    ax.set_xlim(-0.65, len(items) - 0.35)
    ax.set_xticks(total_positions)
    ax.set_xticklabels(total_labels if bottom_row else [""] * len(total_labels))
    style_axis(ax, region, bottom_row)
    region_label_y = 0.80 if region == "FW" else 0.94
    ax.text(
        0.90,
        region_label_y,
        region,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=REGION_LABEL_SIZE,
        fontweight="bold",
        color="black",
        zorder=8,
    )


def add_legend(ax: plt.Axes) -> None:
    # Matplotlib 按列填充；这个顺序得到与参考图相同的两行显示次序。
    legend_order = ["LAI", "Ta", "Pre", "PM2.5", "RH", "NTL", "VPD", "PAR"]
    label_map = {"PM2.5": r"PM$_{2.5}$"}
    handles = [
        Patch(facecolor=FACTOR_COLORS[name], edgecolor="none", label=label_map.get(name, name))
        for name in legend_order
    ]
    ax.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0.01, 1.005),
        ncol=4,
        frameon=False,
        handlelength=1.9,
        handleheight=1.0,
        handletextpad=0.35,
        columnspacing=0.8,
        borderaxespad=0,
        labelspacing=0.55,
    )


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)
    arial_path = font_manager.findfont(
        font_manager.FontProperties(family="Arial"), fallback_to_default=False
    )
    if "arial" not in Path(arial_path).stem.lower():
        raise RuntimeError(f"Arial 字体未正确解析: {arial_path}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    region_items = {
        region: load_region_items(region)
        for row in REGION_GRID
        for region in row
    }
    for region in [r for row in REGION_GRID for r in row]:
        for message in reconciliation_report(region, region_items[region]):
            print(message)

    # 采用参考图的物理画布比例；在不缩小 16 pt 字号的情况下保留足够的图例和标注空间。
    fig, axes = plt.subplots(4, 2, figsize=(12.63, 18.65), facecolor="white")
    fig.subplots_adjust(
        left=0.105,
        right=0.985,
        bottom=0.060,
        top=0.985,
        wspace=0.22,
        hspace=0.055,
    )

    for row_index, region_pair in enumerate(REGION_GRID):
        for column_index, region in enumerate(region_pair):
            draw_waterfall(
                axes[row_index, column_index],
                region,
                region_items[region],
                bottom_row=(row_index == len(REGION_GRID) - 1),
            )
    add_legend(axes[0, 0])

    stem = OUTPUT_DIR / "Figure5_实际贡献瀑布图_统一样式"
    require_matplotlib_panel_alignment(
        fig,
        axes=list(axes.flat),
        panel_ids=[region for row in REGION_GRID for region in row],
        json_out=stem.with_suffix(".alignment.json"),
        overlay_svg=stem.with_suffix(".alignment.svg"),
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        require_panel_labels=False,
        strict=True,
    )
    fig.savefig(stem.with_suffix(".png"), dpi=DPI, facecolor="white")
    fig.savefig(stem.with_suffix(".pdf"), dpi=DPI, facecolor="white")
    fig.savefig(stem.with_suffix(".svg"), facecolor="white")
    plt.close(fig)
    print(f"saved: {stem.with_suffix('.png')}")
    print(f"saved: {stem.with_suffix('.pdf')}")
    print(f"saved: {stem.with_suffix('.svg')}")


if __name__ == "__main__":
    main()
