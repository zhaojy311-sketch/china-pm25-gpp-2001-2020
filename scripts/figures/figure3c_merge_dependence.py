from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "review_required" / "figure3" / "Figure3c_original.png"
HIGH_RES_THIRD_SOURCE = (
    ROOT / "data" / "review_required" / "figure3" / "Figure3c_unified_4400x1814.png"
)
THIRD_OUTPUT_DIR = ROOT / "outputs" / "figure3c"
COMBINED_OUTPUT_DIR = ROOT / "outputs" / "figure3_combined"

FIGURE_A = (
    ROOT
    / "outputs"
    / "figure3a"
    / "驱动因子贡献率空间分布_精简标签_统一字号.png"
)
FIGURE_B = (
    ROOT
    / "outputs"
    / "figure3b"
    / "SHAP_regional_facets_locator_R.png"
)

ARIAL = Path(r"C:\Windows\Fonts\arial.ttf")
ARIAL_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")
CHINESE_FONT = Path(r"C:\Windows\Fonts\msyh.ttc")

# 合并时 A、B 会按共同高度缩放；其正文在最终画布上约为 63--67 px。
# C 使用 64 px Arial，使三部分在同等显示尺寸下视觉字号一致。
FONT_SIZE = 64
PANEL_WIDTH = 1280
PANEL_HEIGHT = 960
PLOT_SIZE = 640
LEFT_MARGIN = 330
TOP_MARGIN = 110
COLORBAR_GAP = 45
COLORBAR_WIDTH = 28
COLUMN_GAP = 16
ROW_GAP = 24
OUTER_X = 30
OUTER_Y = 26
COMBINED_DPI = 600
THIRD_COMBINED_WIDTH = 5228
TICK_LENGTH = 7
TICK_WIDTH = 2


@dataclass(frozen=True)
class PanelSpec:
    plot_box: tuple[int, int, int, int]
    colorbar_box: tuple[int, int, int, int]
    x_ticks: tuple[str, ...]
    y_ticks: tuple[str, ...]
    x_label: str
    colorbar_ticks: tuple[str, ...]
    exponent: int


PANELS = (
    PanelSpec((67, 10, 201, 143), (218, 25, 222, 128),
              ("0", "2", "4", "6"), ("-800", "-400", "0", "400", "800", "1200"),
              "LAI(m²/m²)", ("0", "2", "3", "5"), -3),
    PanelSpec((284, 10, 419, 143), (436, 24, 440, 128),
              ("260", "280", "300"), ("-600", "-300", "0", "300", "600"),
              "Ta(K)", ("0", "2", "3", "5"), -4),
    PanelSpec((497, 10, 631, 143), (648, 25, 652, 128),
              ("0", "1000", "2000", "3000"), ("-400", "0", "400", "800"),
              "Pre(mm)", ("0", "1", "1", "2"), -5),
    PanelSpec((717, 10, 852, 143), (868, 24, 872, 128),
              ("10", "30", "50", "70", "90", "110"), ("-600", "-300", "0", "300", "600"),
              "PM2.5(μg/m³)", ("0", "5", "10", "15"), -4),
    PanelSpec((67, 191, 201, 325), (218, 206, 222, 309),
              ("20", "40", "60", "80", "100"), ("-500", "-250", "0", "250"),
              "RH(%)", ("0", "3", "6", "10"), -4),
    PanelSpec((284, 191, 419, 325), (436, 206, 440, 310),
              ("0", "0.7", "1.4"), ("-300", "-150", "0", "150", "300"),
              "VPD(kPa)", ("0", "2", "5", "7"), -2),
    PanelSpec((496, 191, 630, 325), (647, 206, 651, 310),
              ("45", "60", "75", "90", "115"), ("-400", "-200", "0", "200"),
              "PAR(W/m²)", ("0", "4", "9", "13"), -4),
    PanelSpec((717, 191, 851, 325), (868, 206, 872, 309),
              ("0", "2000", "4000", "6000"), ("-600", "-300", "0", "300"),
              "NTL", ("0", "4", "8", "12"), -5),
)


def load_font(size: int, bold: bool = False, chinese: bool = False) -> ImageFont.FreeTypeFont:
    path = CHINESE_FONT if chinese else (ARIAL_BOLD if bold else ARIAL)
    return ImageFont.truetype(str(path), size)


def equally_spaced(start: int, end: int, count: int) -> list[int]:
    if count == 1:
        return [(start + end) // 2]
    return [round(start + index * (end - start) / (count - 1)) for index in range(count)]


def paste_rotated_shap_label(
    canvas: Image.Image,
    center: tuple[int, int],
    font: ImageFont.FreeTypeFont,
) -> None:
    text_layer = Image.new("RGBA", (620, 130), (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    draw.text((10, 10), "SHAP value", font=font, fill="black", anchor="la")
    bbox = text_layer.getbbox()
    if bbox is None:
        return
    rotated = text_layer.crop(bbox).rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
    x = round(center[0] - rotated.width / 2)
    y = round(center[1] - rotated.height / 2)
    canvas.paste(rotated, (x, y), rotated)


def draw_exponent(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    exponent: int,
    font: ImageFont.FreeTypeFont,
) -> None:
    base = "×10"
    exponent_base_font = load_font(round(FONT_SIZE * 0.78))
    draw.text((x, y), base, font=exponent_base_font, fill="black", anchor="ma")
    base_width = draw.textbbox((0, 0), base, font=exponent_base_font)[2]
    exponent_font = load_font(round(FONT_SIZE * 0.55))
    draw.text(
        (x + base_width // 2 - 1, y - round(FONT_SIZE * 0.08)),
        str(exponent),
        font=exponent_font,
        fill="black",
        anchor="lm",
    )


def build_third_figure() -> Image.Image:
    source = Image.open(SOURCE).convert("RGB")
    font = load_font(FONT_SIZE)

    width = 2 * OUTER_X + 4 * PANEL_WIDTH + 3 * COLUMN_GAP
    height = 2 * OUTER_Y + 2 * PANEL_HEIGHT + ROW_GAP
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)

    for index, spec in enumerate(PANELS):
        row, column = divmod(index, 4)
        panel_x = OUTER_X + column * (PANEL_WIDTH + COLUMN_GAP)
        panel_y = OUTER_Y + row * (PANEL_HEIGHT + ROW_GAP)
        plot_x = panel_x + LEFT_MARGIN
        plot_y = panel_y + TOP_MARGIN
        plot_bottom = plot_y + PLOT_SIZE

        plot = source.crop(spec.plot_box).resize(
            (PLOT_SIZE, PLOT_SIZE), Image.Resampling.LANCZOS
        )
        canvas.paste(plot, (plot_x, plot_y))

        colorbar_height = round(PLOT_SIZE * 0.84)
        # Use only the centre colour column.  The original colour bars are just
        # four pixels wide; including their outer pixels also captures the old
        # frame/white margin and makes a widened bar look partly covered.
        bar_source = source.crop(spec.colorbar_box).convert("RGB")
        centre_x = bar_source.width // 2
        colour_column = bar_source.crop(
            (centre_x, 0, centre_x + 1, bar_source.height)
        )
        colorbar = colour_column.resize(
            (COLORBAR_WIDTH, colorbar_height), Image.Resampling.BICUBIC
        )
        colorbar_x = plot_x + PLOT_SIZE + COLORBAR_GAP
        colorbar_y = plot_y + round((PLOT_SIZE - colorbar_height) / 2)
        canvas.paste(colorbar, (colorbar_x, colorbar_y))

        # X、Y 刻度文字在数据框外重新绘制；数据框内部像素保持不变。
        x_tick_positions = equally_spaced(
            plot_x, plot_x + PLOT_SIZE, len(spec.x_ticks)
        )
        for x, label in zip(x_tick_positions, spec.x_ticks):
            # 与 A、B 一致，数值轴刻度统一向外。
            draw.line(
                (x, plot_bottom, x, plot_bottom + TICK_LENGTH),
                fill="#444444",
                width=TICK_WIDTH,
            )
            draw.text((x, plot_bottom + 12), label, font=font, fill="black", anchor="ma")

        y_tick_positions = equally_spaced(
            plot_bottom, plot_y, len(spec.y_ticks)
        )
        for y, label in zip(y_tick_positions, spec.y_ticks):
            draw.line(
                (plot_x - TICK_LENGTH, y, plot_x, y),
                fill="#444444",
                width=TICK_WIDTH,
            )
            draw.text((plot_x - 18, y), label, font=font, fill="black", anchor="rm")

        draw.text(
            (plot_x + PLOT_SIZE // 2, plot_bottom + 100),
            spec.x_label,
            font=font,
            fill="black",
            anchor="ma",
        )

        for y, label in zip(
            equally_spaced(colorbar_y + colorbar_height, colorbar_y, len(spec.colorbar_ticks)),
            spec.colorbar_ticks,
        ):
            draw.line(
                (
                    colorbar_x + COLORBAR_WIDTH,
                    y,
                    colorbar_x + COLORBAR_WIDTH + TICK_LENGTH,
                    y,
                ),
                fill="#444444",
                width=TICK_WIDTH,
            )
            draw.text(
                (colorbar_x + COLORBAR_WIDTH + 20, y),
                label,
                font=font,
                fill="black",
                anchor="lm",
            )

        draw_exponent(
            draw,
            colorbar_x + COLORBAR_WIDTH // 2,
            plot_y - 40,
            spec.exponent,
            font,
        )

        if column == 0:
            paste_rotated_shap_label(
                canvas,
                (panel_x + 55, plot_y + PLOT_SIZE // 2),
                font,
            )

    return canvas


def resize_to_width(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def resize_exact(image: Image.Image, width: int, height: int) -> Image.Image:
    return image.resize((width, height), Image.Resampling.LANCZOS)


def png_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def write_word_svg(third_png: Path, display_width: int) -> Path:
    """Create a self-contained mixed-vector SVG that Word can insert directly."""
    first = Image.open(FIGURE_A)
    second = Image.open(FIGURE_B)
    third = Image.open(third_png)

    first_ratio = first.width / first.height
    second_ratio = second.width / second.height
    display_height = round(third.height * display_width / third.width)
    top_height = round(display_width / (first_ratio + second_ratio))
    first_width = round(top_height * first_ratio)
    second_width = display_width - first_width

    outer_margin = 50
    header_height = 104
    row_gap = 54
    canvas_width = 2 * outer_margin + display_width
    third_header_y = header_height + top_height + row_gap
    third_y = third_header_y + header_height
    canvas_height = third_y + display_height + outer_margin
    second_x = outer_margin + first_width

    # 600 dpi 对应约 225.6 × 216.7 mm。图片均以内嵌 data URI 保存，
    # SVG 是单一文件，移动或插入 Word 时不会丢失外部链接。
    width_mm = canvas_width / COMBINED_DPI * 25.4
    height_mm = canvas_height / COMBINED_DPI * 25.4
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width_mm:.3f}mm" height="{height_mm:.3f}mm"
     viewBox="0 0 {canvas_width} {canvas_height}">
  <title>Combined SHAP contribution figure</title>
  <desc>Word-compatible mixed-vector figure with embedded high-resolution panels.</desc>
  <rect width="100%" height="100%" fill="white"/>
  <image x="{outer_margin}" y="{header_height}" width="{first_width}" height="{top_height}"
         preserveAspectRatio="none" xlink:href="{png_data_uri(FIGURE_A)}"/>
  <image x="{second_x}" y="{header_height}" width="{second_width}" height="{top_height}"
         preserveAspectRatio="none" xlink:href="{png_data_uri(FIGURE_B)}"/>
  <image x="{outer_margin}" y="{third_y}" width="{display_width}" height="{display_height}"
         preserveAspectRatio="none" xlink:href="{png_data_uri(third_png)}"/>
  <g font-family="Arial, sans-serif" font-size="{FONT_SIZE}" font-weight="400" fill="#000">
    <text x="{outer_margin + 10}" y="68" dominant-baseline="middle">(a)</text>
    <text x="{second_x + 10}" y="68" dominant-baseline="middle">(b)</text>
    <text x="{outer_margin + 10}" y="{third_header_y + 68}" dominant-baseline="middle">(c)</text>
  </g>
</svg>
'''
    output = COMBINED_OUTPUT_DIR / "三图合并_abc_Word矢量版.svg"
    output.write_text(svg, encoding="utf-8")
    return output


def build_combined(third: Image.Image) -> Image.Image:
    first = Image.open(FIGURE_A).convert("RGB")
    second = Image.open(FIGURE_B).convert("RGB")

    # 用 C 的宽度作为整个版面的唯一基准。A、B 保持各自宽高比并使用
    # 完全相同的高度，同时令 A 宽 + B 宽 = C 宽。
    first_ratio = first.width / first.height
    second_ratio = second.width / second.height
    top_row_height = round(third.width / (first_ratio + second_ratio))
    first_width = round(top_row_height * first_ratio)
    second_width = third.width - first_width
    first = resize_exact(first, first_width, top_row_height)
    second = resize_exact(second, second_width, top_row_height)

    header_height = 104
    outer_margin = 50
    row_gap = 54
    top_row_width = first.width + second.width
    canvas_width = 2 * outer_margin + third.width
    third_header_y = header_height + top_row_height + row_gap
    third_y = third_header_y + header_height
    total_height = third_y + third.height + outer_margin
    combined = Image.new("RGB", (canvas_width, total_height), "white")
    draw = ImageDraw.Draw(combined)
    label_font = load_font(FONT_SIZE)

    top_row_x = outer_margin
    first_x = top_row_x
    second_x = first_x + first.width
    first_y = header_height
    second_y = header_height
    third_x = outer_margin

    draw.text((first_x + 10, 68), "(a)", font=label_font, fill="black", anchor="lm")
    draw.text((second_x + 10, 68), "(b)", font=label_font, fill="black", anchor="lm")
    draw.text(
        (third_x + 10, third_header_y + 68),
        "(c)",
        font=label_font,
        fill="black",
        anchor="lm",
    )
    combined.paste(first, (first_x, first_y))
    combined.paste(second, (second_x, second_y))
    combined.paste(third, (third_x, third_y))
    return combined


def main() -> None:
    THIRD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    COMBINED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Use the existing 8800 × 3628, 600 dpi redraw instead of enlarging the
    # 900 × 334 screenshot.  The original numerical SHAP arrays are not present
    # in this project, so pixel digitisation would not be scientifically exact.
    high_res_third = Image.open(HIGH_RES_THIRD_SOURCE).convert("RGB")
    third = resize_to_width(high_res_third, THIRD_COMBINED_WIDTH)
    third_png = THIRD_OUTPUT_DIR / "SHAP依赖图_统一字体字号.png"
    third_tif = THIRD_OUTPUT_DIR / "SHAP依赖图_统一字体字号.tif"
    third.save(third_png, dpi=(300, 300), optimize=True)
    third.save(third_tif, dpi=(300, 300), compression="tiff_lzw")

    svg_path = write_word_svg(HIGH_RES_THIRD_SOURCE, third.width)

    combined = build_combined(third)
    combined_png = COMBINED_OUTPUT_DIR / "三图合并_abc.png"
    combined_tif = COMBINED_OUTPUT_DIR / "三图合并_abc.tif"
    # 混合了地图边界、柱形图和散点栅格，按投稿常用的 600 dpi 输出。
    combined.save(combined_png, dpi=(COMBINED_DPI, COMBINED_DPI), optimize=True)
    combined.save(
        combined_tif,
        dpi=(COMBINED_DPI, COMBINED_DPI),
        compression="tiff_lzw",
    )

    print(f"已输出：{third_png}")
    print(f"已输出：{third_tif}")
    print(f"已输出：{combined_png}")
    print(f"已输出：{combined_tif}")
    print(f"已输出：{svg_path}")
    print(f"第三图尺寸：{third.size[0]} × {third.size[1]} px")
    print(f"合并图尺寸：{combined.size[0]} × {combined.size[1]} px")


if __name__ == "__main__":
    main()
