from __future__ import annotations

import io
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


# -----------------------------------------------------------------------------
# 输入、输出与统一样式
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
PPTX_FILE = ROOT / "data" / "review_required" / "figure3" / "Figure3_source.pptx"
OUTPUT_DIR = ROOT / "outputs" / "figure3a"

# PPT 内嵌的 8 张高分辨率原始面板。它们与所给截图的均值和标准差完全对应。
PANELS = [
    ("LAI", "image81.png", "Mean: 43% ± 17%", (20, 50, 80)),
    ("Ta", "image86.png", "Mean: 28% ± 14%", (20, 50, 80)),
    ("Pre", "image84.png", "Mean: 10% ± 8%", (10, 25, 40)),
    ("PM2.5", "image87.png", "Mean: 6% ± 6%", (15, 30, 60)),
    ("RH", "image85.png", "Mean: 5% ± 4%", (10, 25, 40)),
    ("VPD", "image80.png", "Mean: 3% ± 3%", (8, 16, 32)),
    ("PAR", "image83.png", "Mean: 3% ± 3%", (8, 16, 32)),
    ("NTL", "image82.png", "Mean: 3% ± 3%", (15, 30, 60)),
]

# 所有新绘制文字（变量名、均值、经纬度、色带刻度）统一使用同一字号。
FONT_SIZE = 90
FONT_PATHS = [
    Path(r"C:\Windows\Fonts\arial.ttf"),
    Path(r"C:\Windows\Fonts\Arial.ttf"),
]

MAIN_WIDTH = 1350
LEFT_LABEL_MARGIN = 140
COLORBAR_GAP = 16
COLORBAR_WIDTH = 46
COLORBAR_LABEL_MARGIN = 190
PANEL_WIDTH = (
    LEFT_LABEL_MARGIN
    + MAIN_WIDTH
    + COLORBAR_GAP
    + COLORBAR_WIDTH
    + COLORBAR_LABEL_MARGIN
)
OUTER_X = 90
OUTER_Y = 50
COLUMN_GAP = 32
ROW_GAP = 12
BOTTOM_LABEL_MARGIN = 60

# 经纬度范围沿用原图；仅精简显示标签。
MAP_EXTENT = (70.0, 137.0, 17.0, 55.0)
LONGITUDE_LABELS = (80, 100, 120)  # 仅最底行显示
LATITUDE_LABELS = (20, 35, 50)     # 两个间隔；仅左列显示


def load_font() -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if path.exists():
            return ImageFont.truetype(str(path), FONT_SIZE)
    return ImageFont.load_default()


def consecutive_groups(values: np.ndarray) -> list[tuple[int, int]]:
    """把连续整数位置整理为闭区间，供自动识别图框使用。"""
    if len(values) == 0:
        return []
    groups: list[tuple[int, int]] = []
    start = previous = int(values[0])
    for value in values[1:]:
        value = int(value)
        if value != previous + 1:
            groups.append((start, previous))
            start = value
        previous = value
    groups.append((start, previous))
    return groups


def locate_frames(image: Image.Image) -> tuple[tuple[int, int, int, int], tuple[int, int]]:
    """自动定位主图外框和紧邻其右侧的色带。"""
    array = np.asarray(image.convert("RGB"))
    dark = array.max(axis=2) < 80
    height, width = dark.shape

    vertical_groups = consecutive_groups(
        np.flatnonzero(dark.sum(axis=0) > height * 0.62)
    )
    if len(vertical_groups) < 4:
        raise RuntimeError("无法识别主图和色带的竖直边框。")

    x_left = vertical_groups[0][0]
    x_right = vertical_groups[1][1]
    colorbar_left = vertical_groups[2][0]
    colorbar_right = vertical_groups[3][1]

    span = x_right - x_left + 1
    horizontal_groups = consecutive_groups(
        np.flatnonzero(dark[:, x_left : x_right + 1].sum(axis=1) > span * 0.78)
    )
    if len(horizontal_groups) < 2:
        raise RuntimeError("无法识别主图的水平边框。")
    y_top = horizontal_groups[0][0]
    y_bottom = horizontal_groups[-1][1]

    return (x_left, y_top, x_right, y_bottom), (colorbar_left, colorbar_right)


def clean_main_map(main: Image.Image) -> Image.Image:
    """只清除左上角旧标题；不遮盖底部地图和原始 Mean 标注。"""
    cleaned = main.convert("RGB")
    draw = ImageDraw.Draw(cleaned)
    width, height = cleaned.size

    # 标题位于地图外的左上角留白区，因此这里不会覆盖任何空间数据。
    draw.rectangle((12, 6, 820, 205), fill="white")

    # 南海附图原右边框、下边框外侧仅为空白余量。裁去这些余量后，
    # 将该两条边框同时作为主图外框；不使用白块扩展，也不遮挡地图内容。
    crop_right = round(width * 0.985)
    crop_bottom = round(height * 0.981)
    cleaned = cleaned.crop((0, 0, crop_right, crop_bottom))

    # 补齐裁切后主图上半部的右边框和左半部的下边框。边框画在最外侧，
    # 与南海附图既有的右、下边框重合，不进入地图数据区。
    draw = ImageDraw.Draw(cleaned)
    line_width = max(3, round(cleaned.width / 500))
    draw.line(
        (cleaned.width - 1, 0, cleaned.width - 1, cleaned.height - 1),
        fill="#222222",
        width=line_width,
    )
    draw.line(
        (0, cleaned.height - 1, cleaned.width - 1, cleaned.height - 1),
        fill="#222222",
        width=line_width,
    )
    return cleaned


def read_panel(zip_file: zipfile.ZipFile, media_name: str) -> tuple[Image.Image, Image.Image]:
    with zip_file.open(f"ppt/media/{media_name}") as stream:
        original = Image.open(io.BytesIO(stream.read())).convert("RGB")

    (x0, y0, x1, y1), (cb0, cb1) = locate_frames(original)
    main = original.crop((x0, y0, x1 + 1, y1 + 1))
    colorbar = original.crop((cb0, y0, cb1 + 1, y1 + 1))
    return clean_main_map(main), colorbar


def fit_panel_images(main: Image.Image, colorbar: Image.Image) -> tuple[Image.Image, Image.Image]:
    main_height = round(MAIN_WIDTH * main.height / main.width)
    main = main.resize((MAIN_WIDTH, main_height), Image.Resampling.LANCZOS)
    colorbar = colorbar.resize((COLORBAR_WIDTH, main_height), Image.Resampling.LANCZOS)
    return main, colorbar


def longitude_x(main_x: int, longitude: float) -> int:
    west, east, _, _ = MAP_EXTENT
    return round(main_x + (longitude - west) / (east - west) * (MAIN_WIDTH - 1))


def latitude_y(main_y: int, main_height: int, latitude: float) -> int:
    _, _, south, north = MAP_EXTENT
    return round(main_y + (north - latitude) / (north - south) * (main_height - 1))


def draw_tick(draw: ImageDraw.ImageDraw, point: tuple[int, int], horizontal: bool) -> None:
    x, y = point
    if horizontal:
        draw.line((x, y, x, y + 9), fill="#333333", width=3)
    else:
        draw.line((x - 9, y, x, y), fill="#333333", width=3)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    font = load_font()

    prepared: list[tuple[str, str, tuple[int, ...], Image.Image, Image.Image]] = []
    with zipfile.ZipFile(PPTX_FILE) as archive:
        for title, media_name, mean_text, color_ticks in PANELS:
            main_image, colorbar_image = read_panel(archive, media_name)
            main_image, colorbar_image = fit_panel_images(main_image, colorbar_image)
            prepared.append((title, mean_text, color_ticks, main_image, colorbar_image))

    main_height = prepared[0][3].height
    canvas_width = 2 * OUTER_X + 2 * PANEL_WIDTH + COLUMN_GAP
    canvas_height = (
        2 * OUTER_Y
        + 4 * main_height
        + 3 * ROW_GAP
        + BOTTOM_LABEL_MARGIN
    )
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)

    for index, (title, mean_text, color_ticks, main_image, colorbar_image) in enumerate(prepared):
        row, column = divmod(index, 2)
        panel_x = OUTER_X + column * (PANEL_WIDTH + COLUMN_GAP)
        main_x = panel_x + LEFT_LABEL_MARGIN
        main_y = OUTER_Y + row * (main_height + ROW_GAP)
        colorbar_x = main_x + MAIN_WIDTH + COLORBAR_GAP

        canvas.paste(main_image, (main_x, main_y))
        canvas.paste(colorbar_image, (colorbar_x, main_y))
        draw.rectangle(
            (main_x, main_y, main_x + MAIN_WIDTH - 1, main_y + main_height - 1),
            outline="#333333",
            width=4,
        )
        draw.rectangle(
            (
                colorbar_x,
                main_y,
                colorbar_x + COLORBAR_WIDTH - 1,
                main_y + main_height - 1,
            ),
            outline="#333333",
            width=4,
        )

        # 删除 (a)–(h)，变量名与其余新绘制文字使用同一字号。
        # 原始 Mean 标注完整保留，避免清除文字时遮盖底部地图。
        draw.text((main_x + 18, main_y + 14), title, font=font, fill="black", anchor="la")

        # 每个色带仅保留 3 个代表性刻度，减少数字拥挤。
        colorbar_max = {
            "LAI": 100,
            "Ta": 100,
            "Pre": 50,
            "PM2.5": 75,
            "RH": 50,
            "VPD": 40,
            "PAR": 40,
            "NTL": 75,
        }[title]
        for value in color_ticks:
            tick_y = round(main_y + (1.0 - value / colorbar_max) * (main_height - 1))
            draw.line(
                (colorbar_x + COLORBAR_WIDTH, tick_y, colorbar_x + COLORBAR_WIDTH + 9, tick_y),
                fill="#333333",
                width=2,
            )
            draw.text(
                (colorbar_x + COLORBAR_WIDTH + 13, tick_y),
                f"{value}%",
                font=font,
                fill="black",
                anchor="lm",
            )

        # 纬度只放在左列，并由 10° 间隔精简为 15°（20、35、50°N）。
        if column == 0:
            for latitude in LATITUDE_LABELS:
                y = latitude_y(main_y, main_height, latitude)
                draw_tick(draw, (main_x, y), horizontal=False)
                draw.text(
                    (main_x - 14, y),
                    f"{latitude}°N",
                    font=font,
                    fill="black",
                    anchor="rm",
                )

        # 经度只放在最底行，避免每幅子图重复显示。
        if row == 3:
            for longitude in LONGITUDE_LABELS:
                x = longitude_x(main_x, longitude)
                draw_tick(draw, (x, main_y + main_height), horizontal=True)
                draw.text(
                    (x, main_y + main_height + 13),
                    f"{longitude}°E",
                    font=font,
                    fill="black",
                    anchor="ma",
                )

    png_path = OUTPUT_DIR / "驱动因子贡献率空间分布_精简标签_统一字号.png"
    tiff_path = OUTPUT_DIR / "驱动因子贡献率空间分布_精简标签_统一字号.tif"
    canvas.save(png_path, dpi=(300, 300), optimize=True)
    canvas.save(tiff_path, dpi=(300, 300), compression="tiff_lzw")

    print(f"已输出：{png_path}")
    print(f"已输出：{tiff_path}")
    print(f"画布：{canvas_width} × {canvas_height} px；统一字号：{FONT_SIZE} px")


if __name__ == "__main__":
    main()
