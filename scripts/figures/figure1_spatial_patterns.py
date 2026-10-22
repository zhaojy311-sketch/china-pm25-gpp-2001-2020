from __future__ import annotations

import struct
import gc
import sys
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, FuncFormatter

UTILS_DIR = Path(__file__).resolve().parents[1] / "utils"
if str(UTILS_DIR) not in sys.path:
    sys.path.insert(0, str(UTILS_DIR))
from audit_panel_alignment import require_matplotlib_panel_alignment


# -----------------------------------------------------------------------------
# 路径与统一样式
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "review_required"
OUTPUT_DIR = ROOT / "outputs" / "figure1"
QA_DIR = OUTPUT_DIR / "QA"


def locate_input_file(base_name: str) -> Path:
    """兼容工作簿位于项目根目录或“绘图输入数据”子目录的情况。"""
    matches = list((DATA_DIR / "figure1").glob(f"*{base_name}"))
    if len(matches) == 1:
        return matches[0]
    raise FileNotFoundError(f"无法唯一定位输入文件：{base_name}")


MEAN_FILE = DATA_DIR / "figure1" / "Figure1a_2001-2020_mean.xlsx"
TREND_FILE = DATA_DIR / "figure1" / "Figure1b_2001-2020_trend.xlsx"
CORR_FILE = DATA_DIR / "figure1" / "Figure1c-j_driver-GPP_correlations.xlsx"

CHINA_SHP = DATA_DIR / "boundaries" / "china_provinces" / "省界_region.shp"
SOUTH_CHINA_SEA_SHP = DATA_DIR / "boundaries" / "south_china_sea" / "合并文件.shp"

# 全图文字统一字号；11 pt 是当前版式中不遮挡地图和色带的最大稳妥字号。
FONT_SIZE = 11
LARGE_LABEL_SIZE = FONT_SIZE
LARGE_TICK_SIZE = FONT_SIZE
SMALL_LABEL_SIZE = FONT_SIZE
SMALL_TICK_SIZE = FONT_SIZE
TOP_COLORBAR_SIZE = FONT_SIZE
SHARED_COLORBAR_SIZE = FONT_SIZE
PANEL_WIDTH_HEIGHT_RATIO = 1.55
PDF_POINT_DPI = int("200")
SVG_POINT_DPI = int("150")

mpl.rcParams.update(
    {
        "font.family": "Arial",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": FONT_SIZE,
        "axes.labelsize": FONT_SIZE,
        "xtick.labelsize": FONT_SIZE,
        "ytick.labelsize": FONT_SIZE,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.unicode_minus": False,
        "mathtext.fontset": "custom",
        "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold",
    }
)


# -----------------------------------------------------------------------------
# 轻量读取 Shapefile 边界，避免依赖原脚本所在电脑的绝对路径
# -----------------------------------------------------------------------------
def read_shapefile_segments(path: Path) -> list[np.ndarray]:
    """读取 Polygon/Polyline Shapefile，返回可供 LineCollection 使用的线段。"""
    segments: list[np.ndarray] = []
    with path.open("rb") as stream:
        stream.seek(100)  # Shapefile 文件头固定为 100 字节
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
    collection = LineCollection(
        segments,
        colors="#333333",
        linewidths=linewidth,
        zorder=3,
    )
    ax.add_collection(collection)


# -----------------------------------------------------------------------------
# 公共绘图函数
# -----------------------------------------------------------------------------
MAP_EXTENT = (70, 137, 17, 55)
INSET_EXTENT = (105, 125, 5, 25)

GPP_COLORS = ["#E2F7BA", "#DEF073", "#BBD349", "#7AA644", "#4A8649", "#2C6A51"]
GPP_BOUNDS = [0, 500, 1000, 1500, 2000, 2500, 3000]
GPP_CMAP = ListedColormap(GPP_COLORS)
GPP_NORM = BoundaryNorm(GPP_BOUNDS, GPP_CMAP.N)

TREND_CORR_COLORS = [
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
CORR_BOUNDS = [-1.0, -0.75, -0.50, -0.25, 0, 0.25, 0.50, 0.75, 1.0]
TREND_CORR_CMAP = ListedColormap(TREND_CORR_COLORS)
TREND_NORM = BoundaryNorm(TREND_BOUNDS, TREND_CORR_CMAP.N)
CORR_NORM = BoundaryNorm(CORR_BOUNDS, TREND_CORR_CMAP.N)


def lon_formatter(value: float, _position: int) -> str:
    return f"{int(value)}°E"


def lat_formatter(value: float, _position: int) -> str:
    return f"{int(value)}°N"


def style_map_axis(
    ax: plt.Axes,
    *,
    show_xlabels: bool,
    show_ylabels: bool,
    tick_size: float,
) -> None:
    ax.set_xlim(MAP_EXTENT[0], MAP_EXTENT[1])
    ax.set_ylim(MAP_EXTENT[2], MAP_EXTENT[3])
    ax.set_aspect("auto")
    # 将 zorder < 2.5 的所有数据点合并为单一栅格层，边界和文字继续保持矢量。
    ax.set_rasterization_zorder(2.5)
    ax.set_facecolor("white")
    ax.xaxis.set_major_locator(FixedLocator([80, 100, 120]))
    ax.yaxis.set_major_locator(FixedLocator([20, 30, 40, 50]))
    ax.xaxis.set_major_formatter(FuncFormatter(lon_formatter))
    ax.yaxis.set_major_formatter(FuncFormatter(lat_formatter))
    ax.tick_params(
        axis="both",
        which="major",
        direction="out",
        length=2.5,
        width=0.7,
        pad=1.5,
        labelsize=tick_size,
        labelbottom=show_xlabels,
        labelleft=show_ylabels,
        bottom=True,
        left=True,
    )
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("#333333")


def add_south_china_sea_inset(
    ax: plt.Axes,
    data: pd.DataFrame,
    value_column: str,
    cmap: ListedColormap,
    norm: BoundaryNorm,
    sea_segments: list[np.ndarray],
    significant: pd.DataFrame | None = None,
) -> None:
    # 右、下边框与主图完全重合；缩小后仅占用右下角海域，不遮挡大陆和台湾。
    inset = ax.inset_axes([0.81, 0.0, 0.19, 0.28], zorder=6)
    inset.set_xlim(INSET_EXTENT[0], INSET_EXTENT[1])
    inset.set_ylim(INSET_EXTENT[2], INSET_EXTENT[3])
    inset.set_aspect("auto")
    inset.set_rasterization_zorder(2.5)
    inset.set_facecolor("white")
    draw_boundaries(inset, sea_segments, linewidth=0.35)

    inside = data[
        data["X"].between(INSET_EXTENT[0], INSET_EXTENT[1])
        & data["Y"].between(INSET_EXTENT[2], INSET_EXTENT[3])
    ]
    inset.scatter(
        inside["X"],
        inside["Y"],
        c=inside[value_column],
        cmap=cmap,
        norm=norm,
        s=0.45,
        alpha=0.55,
        linewidths=0,
        zorder=1,
    )

    if significant is not None:
        significant_inside = significant[
            significant["X"].between(INSET_EXTENT[0], INSET_EXTENT[1])
            & significant["Y"].between(INSET_EXTENT[2], INSET_EXTENT[3])
        ]
        inset.scatter(
            significant_inside["X"],
            significant_inside["Y"],
            color="black",
            marker=".",
            s=0.18,
            alpha=0.9,
            linewidths=0,
            zorder=2,
        )

    inset.set_xticks([])
    inset.set_yticks([])
    for spine in inset.spines.values():
        spine.set_linewidth(0.6)
        spine.set_color("#333333")


def add_panel_label(
    ax: plt.Axes,
    label: str,
    *,
    panel_id: str,
    label_size: float,
) -> None:
    ax.text(
        0.02,
        0.965,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=label_size,
        zorder=8,
    )
    # 不可见的单字母锚点仅供最终版式对齐检查识别，不进入成图。
    ax.text(
        0.02,
        0.965,
        panel_id,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=label_size,
        fontweight="bold",
        visible=False,
    )


def draw_value_panel(
    ax: plt.Axes,
    data: pd.DataFrame,
    value_column: str,
    label: str,
    cmap: ListedColormap,
    norm: BoundaryNorm,
    china_segments: list[np.ndarray],
    sea_segments: list[np.ndarray],
    panel_id: str,
    label_size: float,
) -> mpl.collections.PathCollection:
    scatter = ax.scatter(
        data["X"],
        data["Y"],
        c=data[value_column],
        cmap=cmap,
        norm=norm,
        s=0.55,
        alpha=0.55,
        linewidths=0,
        zorder=1,
    )
    draw_boundaries(ax, china_segments, linewidth=0.35)
    add_south_china_sea_inset(
        ax, data, value_column, cmap, norm, sea_segments, significant=None
    )
    add_panel_label(ax, label, panel_id=panel_id, label_size=label_size)
    return scatter


def add_trend_significance_legend(
    ax: plt.Axes,
    data: pd.DataFrame,
    *,
    font_size: float,
) -> None:
    """在趋势图左下角添加正负趋势及显著性占比信息框。"""
    valid_mask = data["GPP_Slope"].notna() & data["P"].notna()
    valid = data.loc[valid_mask, ["GPP_Slope", "P"]]
    total = len(valid)
    if total == 0:
        raise ValueError("趋势数据中没有可用于计算显著性占比的有效记录")

    positive = valid["GPP_Slope"] > 0
    negative = ~positive  # 与原分类代码一致：零变化率归入 Negative。
    significant = valid["P"] < 0.05
    # 与 (b) 的蓝—红趋势色标保持一致：正趋势为红色系，负趋势为蓝色系；
    # 同一方向中以浅色表示不显著、深色表示显著。
    categories = [
        ("Pos(N.S)", positive & ~significant, TREND_CORR_COLORS[5]),
        ("Neg(N.S)", negative & ~significant, TREND_CORR_COLORS[2]),
        ("Pos(P<0.05)", positive & significant, TREND_CORR_COLORS[6]),
        ("Neg(P<0.05)", negative & significant, TREND_CORR_COLORS[1]),
    ]
    handles = [
        Patch(
            facecolor=color,
            edgecolor="none",
            label=f"{name} ({mask.sum() / total * 100:.1f}%)",
        )
        for name, mask, color in categories
    ]
    legend = ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.012, 0.004),
        fontsize=font_size,
        frameon=True,
        facecolor="white",
        edgecolor="black",
        framealpha=1.0,
        handlelength=2.0,
        handleheight=1.0,
        handletextpad=0.35,
        labelspacing=0.05,
        borderpad=0.15,
        borderaxespad=0.0,
    )
    legend.get_frame().set_linewidth(0.6)
    legend.set_zorder(9)


def draw_correlation_panel(
    ax: plt.Axes,
    data: pd.DataFrame,
    label: str,
    china_segments: list[np.ndarray],
    sea_segments: list[np.ndarray],
    panel_id: str,
    label_size: float,
) -> mpl.collections.PathCollection:
    significant = data[data["P"] < 0.05]
    scatter = ax.scatter(
        data["X"],
        data["Y"],
        c=data["Pearson_Correlation"],
        cmap=TREND_CORR_CMAP,
        norm=CORR_NORM,
        s=0.55,
        alpha=0.55,
        linewidths=0,
        zorder=1,
    )
    ax.scatter(
        significant["X"],
        significant["Y"],
        color="black",
        marker=".",
        s=0.18,
        alpha=0.9,
        linewidths=0,
        zorder=2,
    )
    draw_boundaries(ax, china_segments, linewidth=0.35)
    add_south_china_sea_inset(
        ax,
        data,
        "Pearson_Correlation",
        TREND_CORR_CMAP,
        CORR_NORM,
        sea_segments,
        significant=significant,
    )
    add_panel_label(ax, label, panel_id=panel_id, label_size=label_size)
    significant_percent = len(significant) / len(data) * 100
    ax.text(
        0.02,
        0.006,
        f"P < 0.05 ({significant_percent:.1f}%)",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=label_size,
        zorder=8,
    )
    return scatter


def apply_colorbar_style(
    colorbar: mpl.colorbar.Colorbar,
    label: str,
    *,
    font_size: float,
) -> None:
    colorbar.set_label(label, fontsize=font_size, labelpad=4)
    colorbar.ax.tick_params(labelsize=font_size, width=0.6, length=2.5, pad=1.5)
    colorbar.outline.set_linewidth(0.6)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    mean_data = pd.read_excel(MEAN_FILE, sheet_name="Sheet1", usecols=["X", "Y", "GPP"])
    mean_data = mean_data.assign(GPP=mean_data["GPP"] / 10.0)
    trend_data = pd.read_excel(
        TREND_FILE, sheet_name="Sheet1", usecols=["X", "Y", "GPP_Slope", "P"]
    )
    correlation_sheets = {
        sheet: pd.read_excel(
            CORR_FILE,
            sheet_name=sheet,
            usecols=["X", "Y", "Pearson_Correlation", "P"],
        )
        for sheet in ["LAI", "t2m", "Pre", "PM2.5", "RH", "VPD", "PAR", "NTL"]
    }

    china_segments = read_shapefile_segments(CHINA_SHP)
    sea_segments = read_shapefile_segments(SOUTH_CHINA_SEA_SHP)

    # ------------------------------------------------------------------
    # 新排版：第一排 2 个主图；其余 8 个子图为 2 行 × 4 列。
    # 两个主图块与下方四列共用相同的左右边界；所有地图绘图区宽高比一致。
    # ------------------------------------------------------------------
    figure_width = 12.0
    figure_height = 6.75
    fig = plt.figure(figsize=(figure_width, figure_height), facecolor="white")

    left = 0.052
    maps_right = 0.885
    bottom = 0.045
    small_hgap = 0.008
    small_vgap = 0.010
    hero_to_small_gap = 0.012
    hero_center_gap = 0.078

    small_width = (maps_right - left - 3 * small_hgap) / 4
    small_height = (
        small_width * figure_width / PANEL_WIDTH_HEIGHT_RATIO / figure_height
    )
    hero_map_width = (maps_right - left - hero_center_gap) / 2
    hero_map_height = (
        hero_map_width * figure_width / PANEL_WIDTH_HEIGHT_RATIO / figure_height
    )
    small_top_row_bottom = bottom + small_height + small_vgap
    hero_bottom = bottom + 2 * small_height + small_vgap + hero_to_small_gap

    # 两个主图绘图区加中缝的总宽度，严格等于下方四列的总占用宽度。
    total_hero_width = 2 * hero_map_width + hero_center_gap
    total_small_width = 4 * small_width + 3 * small_hgap
    if not np.isclose(total_hero_width, total_small_width, atol=1e-12):
        raise RuntimeError("主图与辅助图的总宽度不一致")

    axes: dict[str, plt.Axes] = {}

    axes["a"] = fig.add_axes([left, hero_bottom, hero_map_width, hero_map_height])
    axes["b"] = fig.add_axes(
        [left + hero_map_width + hero_center_gap, hero_bottom, hero_map_width, hero_map_height]
    )
    style_map_axis(
        axes["a"],
        show_xlabels=False,
        show_ylabels=True,
        tick_size=LARGE_TICK_SIZE,
    )
    style_map_axis(
        axes["b"],
        show_xlabels=False,
        show_ylabels=False,
        tick_size=LARGE_TICK_SIZE,
    )

    small_panel_positions = {
        "c": (0, 0),
        "d": (0, 1),
        "g": (0, 2),
        "h": (0, 3),
        "e": (1, 0),
        "f": (1, 1),
        "i": (1, 2),
        "j": (1, 3),
    }
    for panel_id, (row, column) in small_panel_positions.items():
        panel_left = left + column * (small_width + small_hgap)
        panel_bottom = small_top_row_bottom if row == 0 else bottom
        axes[panel_id] = fig.add_axes(
            [panel_left, panel_bottom, small_width, small_height]
        )
        style_map_axis(
            axes[panel_id],
            show_xlabels=(row == 1),
            show_ylabels=(column == 0),
            tick_size=SMALL_TICK_SIZE,
        )

    for panel_id, axis in axes.items():
        axis.set_gid(panel_id)

    mean_scatter = draw_value_panel(
        axes["a"],
        mean_data,
        "GPP",
        "(a) GPP-Mean",
        GPP_CMAP,
        GPP_NORM,
        china_segments,
        sea_segments,
        panel_id="a",
        label_size=LARGE_LABEL_SIZE,
    )
    trend_scatter = draw_value_panel(
        axes["b"],
        trend_data,
        "GPP_Slope",
        "(b) GPP-Trend",
        TREND_CORR_CMAP,
        TREND_NORM,
        china_segments,
        sea_segments,
        panel_id="b",
        label_size=LARGE_LABEL_SIZE,
    )
    add_trend_significance_legend(
        axes["b"],
        trend_data,
        font_size=FONT_SIZE,
    )

    panel_definitions = [
        ("c", "LAI", "(c) LAI"),
        ("d", "PM2.5", "(d) PM$_{2.5}$"),
        ("g", "RH", "(g) RH"),
        ("h", "VPD", "(h) VPD"),
        ("e", "Pre", "(e) Pre"),
        ("f", "t2m", "(f) Ta"),
        ("i", "PAR", "(i) PAR"),
        ("j", "NTL", "(j) NTL"),
    ]
    correlation_scatter = None
    for panel_id, sheet, label in panel_definitions:
        correlation_scatter = draw_correlation_panel(
            axes[panel_id],
            correlation_sheets[sheet],
            label,
            china_segments,
            sea_segments,
            panel_id=panel_id,
            label_size=SMALL_LABEL_SIZE,
        )

    # 顶部两幅图分别使用原有颜色条。
    top_colorbar_gap = 0.006
    top_colorbar_width = 0.013
    mean_cax = fig.add_axes(
        [
            left + hero_map_width + top_colorbar_gap,
            hero_bottom,
            top_colorbar_width,
            hero_map_height,
        ]
    )
    mean_colorbar = fig.colorbar(mean_scatter, cax=mean_cax, ticks=GPP_BOUNDS)
    mean_colorbar.ax.set_yticklabels(["0", "500", "1000", "1500", "2000", ">2500", ""])
    apply_colorbar_style(
        mean_colorbar,
        "GPP-gC/(m²·yr)",
        font_size=TOP_COLORBAR_SIZE,
    )

    trend_left = left + hero_map_width + hero_center_gap
    right_colorbar_gap = 0.008
    trend_cax = fig.add_axes(
        [
            maps_right + right_colorbar_gap,
            hero_bottom,
            top_colorbar_width,
            hero_map_height,
        ]
    )
    trend_colorbar = fig.colorbar(trend_scatter, cax=trend_cax, ticks=TREND_BOUNDS)
    trend_colorbar.ax.set_yticklabels(["", "<-50", "-20", "-10", "0", "10", "20", ">50", ""])
    apply_colorbar_style(
        trend_colorbar,
        "Trend-gC/(m²·yr²)",
        font_size=TOP_COLORBAR_SIZE,
    )

    # 8 幅相关性图共享一个跨越两行的颜色条。
    corr_cax = fig.add_axes(
        [
            maps_right + right_colorbar_gap,
            bottom,
            0.013,
            2 * small_height + small_vgap,
        ]
    )
    corr_colorbar = fig.colorbar(correlation_scatter, cax=corr_cax, ticks=CORR_BOUNDS)
    corr_colorbar.ax.set_yticklabels(["-1", "-0.75", "-0.50", "-0.25", "0", "0.25", "0.50", "0.75", "1"])
    apply_colorbar_style(
        corr_colorbar,
        "R",
        font_size=SHARED_COLORBAR_SIZE,
    )

    # 核对所有地图绘图区的物理宽高比一致。
    panel_ratios = []
    for axis in axes.values():
        position = axis.get_position()
        panel_ratios.append(
            position.width * figure_width / (position.height * figure_height)
        )
    if not np.allclose(
        panel_ratios,
        PANEL_WIDTH_HEIGHT_RATIO,
        rtol=0,
        atol=1e-10,
    ):
        raise RuntimeError("地图子图的宽高比不一致")

    # 释放读取工作簿产生的中间对象，降低高分辨率导出的峰值内存。
    del mean_data, trend_data, correlation_sheets, china_segments, sea_segments
    gc.collect()
    fig.canvas.draw()
    output_stem = OUTPUT_DIR / "图1_GPP空间分布与相关性_新排版"
    require_matplotlib_panel_alignment(
        fig,
        axes=list(axes.values()),
        panel_ids={axis: panel_id for panel_id, axis in axes.items()},
        row_groups=[
            ["a", "b"],
            ["c", "d", "g", "h"],
            ["e", "f", "i", "j"],
        ],
        column_groups=[
            ["c", "e"],
            ["d", "f"],
            ["g", "i"],
            ["h", "j"],
        ],
        json_out=QA_DIR / "图1_新排版.alignment.json",
        overlay_svg=QA_DIR / "图1_新排版.alignment.svg",
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        require_panel_labels=True,
        strict=True,
    )

    # 点云在 PDF/SVG 中分别以 200/150 dpi 嵌入；边界和文字保持矢量。
    # PNG 使用 600 dpi，用于高分辨率位图输出。
    gc.collect()
    fig.savefig(output_stem.with_suffix(".pdf"), dpi=PDF_POINT_DPI, facecolor="white")
    gc.collect()
    fig.savefig(output_stem.with_suffix(".svg"), dpi=SVG_POINT_DPI, facecolor="white")
    gc.collect()
    png_path = output_stem.with_suffix(".png")
    png_temp_path = OUTPUT_DIR / "figure1_export_temp.png"
    fig.savefig(png_temp_path, dpi=600, facecolor="white")
    png_temp_path.replace(png_path)
    plt.close(fig)

    print(f"已输出：{output_stem.with_suffix('.pdf')}")
    print(f"已输出：{output_stem.with_suffix('.svg')}")
    print(f"已输出：{output_stem.with_suffix('.png')}")


if __name__ == "__main__":
    main()
