from __future__ import annotations

import gc
import shutil
import struct
import sys
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, FuncFormatter, MaxNLocator
from scipy import stats

UTILS_DIR = Path(__file__).resolve().parents[1] / "utils"
if str(UTILS_DIR) not in sys.path:
    sys.path.insert(0, str(UTILS_DIR))
from audit_panel_alignment import require_matplotlib_panel_alignment


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "review_required"
OUTPUT_DIR = ROOT / "outputs" / "figure2"
QA_DIR = OUTPUT_DIR / "QA"

ANNUAL_FILE = DATA_DIR / "figure2" / "regional_annual_means.xlsx"
TREND_FILE = DATA_DIR / "figure1" / "Figure1b_2001-2020_trend.xlsx"
CHINA_SHP = DATA_DIR / "boundaries" / "china_provinces" / "省界_region.shp"
SOUTH_CHINA_SEA_SHP = DATA_DIR / "boundaries" / "south_china_sea" / "合并文件.shp"

# 四张图及总拼图中的所有文字统一使用该字号。
FONT_SIZE = 16
DPI = 600

mpl.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 16,
        "axes.labelsize": 16,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
        "legend.fontsize": 16,
        "mathtext.fontset": "custom",
        "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold",
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        # SVG 中保留文字对象，便于在 Illustrator/Inkscape 中继续编辑。
        "svg.fonttype": "none",
    }
)


REGION_ORDER = ["FW", "NW", "CSC", "NE", "NC", "SWC", "EC", "SC"]
LINE_GRID = [["FW", "NE"], ["NW", "NC"], ["SWC", "EC"], ["CSC", "SC"]]

VARIABLE_STYLES = {
    "LAI": {"color": "#2457A6", "marker": "o", "label": "LAI"},
    "PAR": {"color": "#CB0505", "marker": "s", "label": "PAR"},
    "PM2.5": {"color": "#8B2DB2", "marker": "^", "label": r"PM$_{2.5}$"},
    "pre": {"color": "#FF7F00", "marker": "D", "label": "Pre"},
    "RH": {"color": "#00BFC4", "marker": "v", "label": "RH"},
    "t2m": {"color": "#FFC400", "marker": "p", "label": "Ta"},
    "VPD": {"color": "#A0522D", "marker": "h", "label": "VPD"},
    "NTL": {"color": "#62F000", "marker": "d", "label": "NTL"},
}

# 按用户提供的原图位置数字化得到的示意矩形（经度、纬度、宽、高）。
# 这些框用于复现原图版式，不代表行政区边界或严格的空间掩膜。
REGION_BOXES = {
    # 依据用户提供的参考地图逐框反算得到（经度、纬度、宽、高）。
    "NW": (89.5, 32.6, 11.4, 6.0),
    "FW": (101.3, 32.4, 9.7, 7.4),
    "NC": (111.7, 33.9, 9.5, 9.2),
    "NE": (121.1, 43.9, 9.0, 7.4),
    "SWC": (88.0, 24.6, 13.9, 6.4),
    "CSC": (102.6, 25.5, 10.4, 6.4),
    "EC": (113.6, 25.6, 7.6, 7.5),
    "SC": (106.7, 19.1, 10.5, 5.3),
}

TREND_COLORS = [
    "#134B87",
    "#3685BB",
    "#74B0D2",
    "#C1DDE9",
    "#FBE3D6",
    "#F5AC8B",
    "#C6403D",
    "#780522",
]
TREND_BOUNDS = [-100, -50, -20, -10, 0, 10, 20, 50, 100]
TREND_CMAP = ListedColormap(TREND_COLORS)
TREND_NORM = BoundaryNorm(TREND_BOUNDS, TREND_CMAP.N)


def read_shapefile_segments(path: Path) -> list[np.ndarray]:
    segments: list[np.ndarray] = []
    with path.open("rb") as stream:
        stream.seek(100)
        while True:
            record_header = stream.read(8)
            if len(record_header) < 8:
                break
            _, content_length_words = struct.unpack(">2i", record_header)
            content = stream.read(content_length_words * 2)
            if len(content) < 4:
                continue
            shape_type = struct.unpack_from("<i", content, 0)[0]
            if shape_type == 0:
                continue
            if shape_type not in {3, 5, 13, 15, 23, 25}:
                raise ValueError(f"不支持的 Shapefile shape type: {shape_type}")
            num_parts, num_points = struct.unpack_from("<2i", content, 36)
            parts_offset = 44
            parts = list(struct.unpack_from(f"<{num_parts}i", content, parts_offset))
            points_offset = parts_offset + 4 * num_parts
            point_values = struct.unpack_from(
                f"<{num_points * 2}d", content, points_offset
            )
            points = np.asarray(point_values, dtype=float).reshape(-1, 2)
            for part_index, start in enumerate(parts):
                end = parts[part_index + 1] if part_index + 1 < num_parts else num_points
                if end - start >= 2:
                    segments.append(points[start:end])
    return segments


def draw_boundaries(ax: plt.Axes, segments: list[np.ndarray], linewidth: float) -> None:
    ax.add_collection(
        LineCollection(
            segments,
            colors="#333333",
            linewidths=linewidth,
            zorder=4,
        )
    )


def lon_formatter(value: float, _position: int) -> str:
    return f"{int(value)}°E"


def lat_formatter(value: float, _position: int) -> str:
    return f"{int(value)}°N"


def style_spines(ax: plt.Axes, linewidth: float = 0.9) -> None:
    for spine in ax.spines.values():
        spine.set_linewidth(linewidth)
        spine.set_color("#333333")
    ax.tick_params(axis="both", which="major", width=linewidth, length=3.2, pad=8)


def add_panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        0.018,
        0.972,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FONT_SIZE,
        zorder=20,
    )


def load_region_data() -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for region in REGION_ORDER:
        frame = pd.read_excel(ANNUAL_FILE, sheet_name=f"{region}-1")
        frame.columns = [str(column).replace("均值", "").strip() for column in frame.columns]
        frame = frame.rename(columns={frame.columns[0]: "Year"})
        frames[region] = frame
    return frames


def draw_map(
    ax: plt.Axes,
    cax: plt.Axes,
    trend_data: pd.DataFrame,
    china_segments: list[np.ndarray],
    sea_segments: list[np.ndarray],
    panel_label: str,
    rasterize_points: bool = False,
) -> None:
    scatter = ax.scatter(
        trend_data["X"],
        trend_data["Y"],
        c=trend_data["GPP_Slope"],
        cmap=TREND_CMAP,
        norm=TREND_NORM,
        s=0.72,
        # 不再与白色背景进行半透明混合，避免地图出现“白膜/虚化”感。
        # 色表及分级仍与原 GPP-Trend 图完全一致。
        alpha=1.0,
        linewidths=0,
        rasterized=rasterize_points,
        zorder=1,
    )
    draw_boundaries(ax, china_segments, linewidth=0.42)

    ax.set_xlim(70, 137)
    ax.set_ylim(17, 55)
    ax.set_aspect("auto")
    ax.set_facecolor("white")
    ax.xaxis.set_major_locator(FixedLocator([80, 100, 120]))
    ax.yaxis.set_major_locator(FixedLocator([20, 30, 40, 50]))
    ax.xaxis.set_major_formatter(FuncFormatter(lon_formatter))
    ax.yaxis.set_major_formatter(FuncFormatter(lat_formatter))
    ax.tick_params(labelsize=FONT_SIZE, pad=2)
    style_spines(ax)

    box_color = "#003CFF"
    for region, (x, y, width, height) in REGION_BOXES.items():
        ax.add_patch(
            Rectangle(
                (x, y),
                width,
                height,
                fill=False,
                edgecolor=box_color,
                linewidth=1.3,
                zorder=8,
            )
        )
        ax.text(
            x + width / 2,
            y + height / 2,
            region,
            color=box_color,
            fontsize=FONT_SIZE,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=9,
            # 常规 PDF/SVG 中将区域缩写按 600 dpi 栅格嵌入，避免省界线穿字；
            # Word 兼容版已把文字整体转轮廓，因此这里保持矢量，节省内存。
            rasterized=not rasterize_points,
        )

    inset = ax.inset_axes([0.81, 0.0, 0.19, 0.29], zorder=10)
    inset.set_xlim(105, 125)
    inset.set_ylim(5, 25)
    inset.set_aspect("auto")
    inside = trend_data[
        trend_data["X"].between(105, 125) & trend_data["Y"].between(5, 25)
    ]
    inset.scatter(
        inside["X"],
        inside["Y"],
        c=inside["GPP_Slope"],
        cmap=TREND_CMAP,
        norm=TREND_NORM,
        s=0.72,
        alpha=1.0,
        linewidths=0,
        rasterized=rasterize_points,
        zorder=1,
    )
    draw_boundaries(inset, sea_segments, linewidth=0.35)
    inset.set_xticks([])
    inset.set_yticks([])
    style_spines(inset, linewidth=0.65)

    colorbar = ax.figure.colorbar(
        scatter,
        cax=cax,
        orientation="horizontal",
        ticks=[-50, -20, -10, 0, 10, 20, 50],
    )
    colorbar.ax.set_xticklabels(["<-50", "-20", "-10", "0", "10", "20", ">50"])
    colorbar.ax.tick_params(labelsize=FONT_SIZE, width=0.7, length=3, pad=2)
    colorbar.outline.set_linewidth(0.7)
    colorbar.set_label(r"Trend-gC/(m$^2$·yr$^2$)", fontsize=FONT_SIZE, labelpad=2)
    add_panel_label(ax, panel_label)


def period_regression(frame: pd.DataFrame, variable: str, start: int, end: int):
    period = frame[frame["Year"].between(start, end)]
    return stats.linregress(period["Year"].to_numpy(), period[variable].to_numpy())


def significance_label(p_value: float) -> str:
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    return ""


def draw_bar_chart(
    ax: plt.Axes,
    frames: dict[str, pd.DataFrame],
    variable: str,
    colors: tuple[str, str],
    ylabel: str,
    panel_label: str,
    ylim: tuple[float, float],
) -> None:
    first = [period_regression(frames[r], variable, 2001, 2013) for r in REGION_ORDER]
    second = [period_regression(frames[r], variable, 2013, 2020) for r in REGION_ORDER]
    x = np.arange(len(REGION_ORDER), dtype=float)
    width = 0.36
    bars1 = ax.bar(
        x - width / 2,
        [result.slope for result in first],
        width,
        color=colors[0],
        edgecolor="none",
        linewidth=0,
        label="2001–2013",
        zorder=3,
    )
    bars2 = ax.bar(
        x + width / 2,
        [result.slope for result in second],
        width,
        color=colors[1],
        edgecolor="none",
        linewidth=0,
        label="2013–2020",
        zorder=3,
    )

    yrange = ylim[1] - ylim[0]
    for series_index, (bars, results) in enumerate([(bars1, first), (bars2, second)]):
        for bar_index, (bar, result) in enumerate(zip(bars, results)):
            text = significance_label(result.pvalue)
            if not text:
                continue
            height = bar.get_height()
            # 保持符号贴近柱顶，同时避开左上角子图编号与上边界。
            offset = 0.015 * yrange
            text_x = bar.get_x() + bar.get_width() / 2
            text_y = height + offset if height >= 0 else height - offset
            text_va = "bottom" if height >= 0 else "top"
            if variable == "PM2.5" and series_index == 0 and bar_index == 0:
                text_x += 0.35
            if variable == "PM2.5" and series_index == 1 and height < 0:
                # 第二时期负向柱的显著性符号置于浅蓝柱内，避免与底部图例相碰。
                text_y = height + 0.12 * yrange
                text_va = "bottom"
            ax.text(
                text_x,
                text_y,
                text,
                ha="center",
                va=text_va,
                fontsize=FONT_SIZE,
                zorder=6,
            )

    ax.axhline(0, color="#333333", linewidth=0.8, zorder=2)
    ax.set_xlim(-0.55, len(REGION_ORDER) - 0.45)
    ax.set_ylim(*ylim)
    ax.set_xticks(x)
    ax.set_xticklabels(REGION_ORDER)
    ax.set_ylabel(ylabel, labelpad=6)
    if variable == "PM2.5":
        legend_kwargs = {"loc": "lower right", "bbox_to_anchor": (0.99, 0.01)}
        legend_columns = 2
    else:
        legend_kwargs = {"loc": "upper center", "bbox_to_anchor": (0.53, 1.0)}
        legend_columns = 1
    ax.legend(
        frameon=False,
        ncol=legend_columns,
        handlelength=1.6,
        borderaxespad=0.35,
        **legend_kwargs,
    )
    ax.grid(False)
    style_spines(ax)
    add_panel_label(ax, panel_label)


def growth_rate_series(frame: pd.DataFrame, variable: str) -> tuple[np.ndarray, np.ndarray]:
    years = frame["Year"].to_numpy(dtype=float)
    early = frame[frame["Year"].between(2001, 2013)]
    late = frame[frame["Year"].between(2013, 2020)]
    early_coef = np.polyfit(early["Year"], early[variable], 1)
    late_coef = np.polyfit(late["Year"], late[variable], 1)
    early_fit = np.polyval(early_coef, years)
    late_fit = np.polyval(late_coef, years)
    fitted = np.where(years <= 2013, early_fit, late_fit)

    valid_years: list[float] = []
    ratios: list[float] = []
    for index in range(1, len(years)):
        if years[index] == 2014:
            continue
        valid_years.append(years[index])
        ratios.append((fitted[index] - fitted[index - 1]) / fitted[index - 1] * 100)
    return np.asarray(valid_years), np.asarray(ratios)


def draw_line_grid(
    fig: plt.Figure,
    axes: np.ndarray,
    frames: dict[str, pd.DataFrame],
    panel_label: str,
    shared_axis: plt.Axes,
) -> None:
    variable_order = ["LAI", "NTL", "PAR", "PM2.5", "pre", "RH", "t2m", "VPD"]
    for row, region_pair in enumerate(LINE_GRID):
        for col, region in enumerate(region_pair):
            ax = axes[row, col]
            all_ratios: list[float] = []
            for variable in variable_order:
                years, ratios = growth_rate_series(frames[region], variable)
                all_ratios.extend(ratios.tolist())
                style = VARIABLE_STYLES[variable]
                ax.plot(
                    years,
                    ratios,
                    color=style["color"],
                    linestyle="--",
                    linewidth=1.4,
                    alpha=0.90,
                    zorder=2,
                )
                ax.scatter(
                    years,
                    ratios,
                    color=style["color"],
                    marker=style["marker"],
                    s=32,
                    edgecolors="none",
                    label=style["label"],
                    zorder=3,
                )

            minimum = min(all_ratios + [0.0])
            maximum = max(all_ratios + [0.0])
            span = max(maximum - minimum, 1.0)
            ax.set_ylim(minimum - span * 0.08, maximum + span * 0.10)
            ax.set_xlim(2000, 2021)
            ax.axhline(0, color="#333333", linewidth=0.7, zorder=1)
            ax.axvline(2013, color="#FF3030", linestyle="--", linewidth=0.9, zorder=1)
            ax.set_xticks([2001, 2013, 2020])
            if row < 3:
                ax.set_xticklabels([])
            else:
                ax.set_xticklabels(["2001", "2013", "2020"])
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
            ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _pos: f"{value:.0f}%"))
            ax.grid(False)
            style_spines(ax)
            ax.tick_params(axis="y", length=0, pad=14)
            ax.text(
                0.90,
                0.96,
                region,
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=FONT_SIZE,
            )

    add_panel_label(axes[0, 0], panel_label)
    axes[0, 0].legend(
        loc="lower left",
        bbox_to_anchor=(0.03, 0.04),
        frameon=False,
        ncol=2,
        handlelength=1.0,
        handletextpad=0.25,
        columnspacing=0.45,
        borderaxespad=0,
        markerscale=1.0,
    )

    shared_axis.set_frame_on(False)
    shared_axis.patch.set_alpha(0)
    shared_axis.set_xticks([])
    shared_axis.set_yticks([])
    shared_axis.tick_params(
        labelcolor="none", top=False, bottom=False, left=False, right=False
    )
    shared_axis.set_xlabel("Year", labelpad=28)
    shared_axis.set_ylabel("Annual Growth Rate (%)", labelpad=52)


def save_figure(fig: plt.Figure, base_path: Path) -> None:
    """同一画布同时保存高分辨率 PNG、SVG 和 PDF。"""
    # 不使用 Path.with_suffix，避免文件名中的“PM2.5”被误识别为扩展名。
    output_paths = {
        "png": base_path.parent / f"{base_path.name}.png",
        "svg": base_path.parent / f"{base_path.name}.svg",
        "pdf": base_path.parent / f"{base_path.name}.pdf",
    }
    # 先写矢量文件，再写大尺寸 PNG，避免 600 dpi 位图画布占用内存后影响 PDF。
    # PDF/SVG 主体为矢量，仅少量防穿字标签按 300 dpi 嵌入。
    fig.savefig(output_paths["pdf"], format="pdf", dpi=300, facecolor="white")
    fig.savefig(output_paths["svg"], format="svg", dpi=300, facecolor="white")
    # 保留预设画布尺寸，确保左侧三张独立图的像素宽度完全一致。
    fig.savefig(output_paths["png"], dpi=DPI, facecolor="white")
    plt.close(fig)
    gc.collect()
    for output_path in output_paths.values():
        print(f"saved: {output_path}")


def make_map_figure(
    trend_data: pd.DataFrame,
    china_segments: list[np.ndarray],
    sea_segments: list[np.ndarray],
) -> None:
    fig = plt.figure(figsize=(6.9, 4.7), facecolor="white")
    grid = fig.add_gridspec(
        2,
        1,
        height_ratios=[1.0, 0.085],
        left=0.11,
        right=0.98,
        bottom=0.14,
        top=0.98,
        hspace=0.22,
    )
    ax = fig.add_subplot(grid[0])
    cax = fig.add_subplot(grid[1])
    draw_map(ax, cax, trend_data, china_segments, sea_segments, "(a)")
    save_figure(fig, OUTPUT_DIR / "01_GPP趋势与八大区域框")


def make_bar_figure(
    frames: dict[str, pd.DataFrame],
    variable: str,
    colors: tuple[str, str],
    ylabel: str,
    label: str,
    ylim: tuple[float, float],
    filename: str,
) -> None:
    fig, ax = plt.subplots(figsize=(6.9, 3.6), facecolor="white")
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.20, top=0.94)
    draw_bar_chart(ax, frames, variable, colors, ylabel, label, ylim)
    save_figure(fig, OUTPUT_DIR / filename)


def make_line_figure(frames: dict[str, pd.DataFrame]) -> None:
    fig = plt.figure(figsize=(10.6, 12.0), facecolor="white")
    grid = fig.add_gridspec(
        4,
        2,
        left=0.13,
        right=0.99,
        bottom=0.07,
        top=0.99,
        wspace=0.20,
        hspace=0.055,
    )
    axes = np.asarray(
        [[fig.add_subplot(grid[row, col]) for col in range(2)] for row in range(4)]
    )
    shared = fig.add_subplot(grid[:, :])
    draw_line_grid(fig, axes, frames, "(d)", shared)
    shared.set_zorder(-1)
    panel_ids = ["fw", "ne", "nw", "nc", "swc", "ec", "csc", "sc"]
    require_matplotlib_panel_alignment(
        fig,
        axes=list(axes.flat),
        panel_ids=panel_ids,
        row_groups=[["fw", "ne"], ["nw", "nc"], ["swc", "ec"], ["csc", "sc"]],
        column_groups=[["fw", "nw", "swc", "csc"], ["ne", "nc", "ec", "sc"]],
        json_out=QA_DIR / "04_折线图_alignment.json",
        overlay_svg=QA_DIR / "04_折线图_alignment.svg",
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        strict=True,
    )
    save_figure(fig, OUTPUT_DIR / "04_八大区域年增长率折线图")


def make_composite(
    frames: dict[str, pd.DataFrame],
    trend_data: pd.DataFrame,
    china_segments: list[np.ndarray],
    sea_segments: list[np.ndarray],
    word_compatible: bool = False,
) -> None:
    # 保持原来的宽高比例；适度缩小物理画布以便稳定导出 600 dpi
    # （最终仍为约 9600 × 7260 px，满足高分辨率排版）。
    fig = plt.figure(figsize=(16.0, 12.1), facecolor="white")
    outer = fig.add_gridspec(
        1,
        2,
        width_ratios=[0.37, 0.63],
        left=0.055,
        right=0.99,
        bottom=0.055,
        top=0.985,
        wspace=0.16,
    )
    left = outer[0].subgridspec(
        3,
        1,
        height_ratios=[1.25, 0.95, 0.95],
        hspace=0.22,
    )
    map_grid = left[0].subgridspec(2, 1, height_ratios=[1.0, 0.085], hspace=0.22)
    map_ax = fig.add_subplot(map_grid[0])
    map_cax = fig.add_subplot(map_grid[1])
    pm_ax = fig.add_subplot(left[1])
    gpp_ax = fig.add_subplot(left[2])

    draw_map(
        map_ax,
        map_cax,
        trend_data,
        china_segments,
        sea_segments,
        "(a)",
        rasterize_points=word_compatible,
    )
    draw_bar_chart(
        pm_ax,
        frames,
        "PM2.5",
        ("#D62728", "#8FC5E8"),
        r"PM$_{2.5}$ Trend-µg/(m$^3$·yr)",
        "(b)",
        (-6, 2.4),
    )
    draw_bar_chart(
        gpp_ax,
        frames,
        "GPP",
        ("#2E8B57", "#A8D5A2"),
        r"GPP Trend-gC/(m$^2$·yr$^2$)",
        "(c)",
        (0, 31.5),
    )

    right = outer[1].subgridspec(4, 2, wspace=0.20, hspace=0.055)
    line_axes = np.asarray(
        [[fig.add_subplot(right[row, col]) for col in range(2)] for row in range(4)]
    )
    shared = fig.add_subplot(outer[1])
    draw_line_grid(fig, line_axes, frames, "(d)", shared)
    shared.set_zorder(-1)
    line_ids = ["fw", "ne", "nw", "nc", "swc", "ec", "csc", "sc"]
    alignment_tag = "05_总图_Word兼容" if word_compatible else "05_总图"
    require_matplotlib_panel_alignment(
        fig,
        axes=[pm_ax, gpp_ax, *list(line_axes.flat)],
        panel_ids=["pm", "gpp", *line_ids],
        row_groups=[["fw", "ne"], ["nw", "nc"], ["swc", "ec"], ["csc", "sc"]],
        column_groups=[
            ["pm", "gpp"],
            ["fw", "nw", "swc", "csc"],
            ["ne", "nc", "ec", "sc"],
        ],
        json_out=QA_DIR / f"{alignment_tag}_alignment.json",
        overlay_svg=QA_DIR / f"{alignment_tag}_alignment.svg",
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        strict=True,
    )
    if word_compatible:
        word_svg = OUTPUT_DIR / "06_四图拼接总图_Word兼容高精度.svg"
        # Word 对超大量 SVG 散点及外部字体引用兼容性较差：地图像元层按
        # 600 dpi 嵌入，文字转轮廓；其余线条、坐标轴、柱体和标记保持矢量。
        with mpl.rc_context({"svg.fonttype": "path"}):
            # Word 兼容版主体保持矢量，地图像元层以 300 dpi 嵌入即可兼顾清晰度与稳定性。
            fig.savefig(word_svg, format="svg", dpi=300, facecolor="white")
        plt.close(fig)
        gc.collect()
        print(f"saved: {word_svg}")
    else:
        save_figure(fig, OUTPUT_DIR / "05_四图拼接总图")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)
    frames = load_region_data()
    trend_data = pd.read_excel(
        TREND_FILE,
        sheet_name="Sheet1",
        usecols=["X", "Y", "GPP_Slope", "P"],
    )
    china_segments = read_shapefile_segments(CHINA_SHP)
    sea_segments = read_shapefile_segments(SOUTH_CHINA_SEA_SHP)

    make_map_figure(trend_data, china_segments, sea_segments)
    make_bar_figure(
        frames,
        "PM2.5",
        ("#D62728", "#8FC5E8"),
        r"PM$_{2.5}$ Trend-µg/(m$^3$·yr)",
        "(b)",
        (-6, 2.4),
        "02_PM2.5双时期变化趋势柱状图",
    )
    make_bar_figure(
        frames,
        "GPP",
        ("#2E8B57", "#A8D5A2"),
        r"GPP Trend-gC/(m$^2$·yr$^2$)",
        "(c)",
        (0, 31.5),
        "03_GPP双时期变化趋势柱状图",
    )
    make_line_figure(frames)
    make_composite(frames, trend_data, china_segments, sea_segments)
    make_composite(
        frames,
        trend_data,
        china_segments,
        sea_segments,
        word_compatible=True,
    )

    # 保存本次实际使用的代码副本，保证输出图片与脚本版本一致。
    script_copy = OUTPUT_DIR / "00_图2-八大区域变化组合图_绘图代码.py"
    shutil.copy2(Path(__file__), script_copy)
    print(f"saved: {script_copy}")

    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
