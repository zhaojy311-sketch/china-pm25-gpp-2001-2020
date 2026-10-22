from __future__ import annotations

import base64
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PPTX = ROOT / "data" / "review_required" / "figure3" / "Figure3c_source.pptx"
OUTPUT_DIR = ROOT / "outputs" / "figure3c_extracted"
SVG_ENTRY = "ppt/media/image23.svg"
FIGURE3C_SVG = ROOT / "data" / "review_required" / "figure3" / "Figure3c_Arial_article_style.svg"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(PPTX) as archive:
        svg_bytes = archive.read(SVG_ENTRY)

    svg_path = OUTPUT_DIR / "PPT内嵌原始SHAP图.svg"
    svg_path.write_bytes(svg_bytes)

    svg_text = svg_bytes.decode("utf-8")
    match = re.search(r"data:image/(png|jpeg);base64,([^\"]+)", svg_text)
    if match is None:
        raise RuntimeError("The SVG does not contain an embedded raster image.")
    extension = "png" if match.group(1) == "png" else "jpg"
    raster_path = OUTPUT_DIR / f"PPT内嵌原始SHAP图层.{extension}"
    raster_path.write_bytes(base64.b64decode(match.group(2)))

    figure3c_text = FIGURE3C_SVG.read_text(encoding="utf-8")
    figure3c_match = re.search(
        r"data:image/(png|jpeg);base64,([^\"]+)", figure3c_text
    )
    if figure3c_match is None:
        raise RuntimeError("Figure3c SVG does not contain an embedded raster image.")
    figure3c_extension = "png" if figure3c_match.group(1) == "png" else "jpg"
    figure3c_raster = OUTPUT_DIR / f"Figure3c_无文字高分辨率底图.{figure3c_extension}"
    figure3c_raster.write_bytes(base64.b64decode(figure3c_match.group(2)))

    print(f"Extracted: {svg_path}")
    print(f"Extracted: {raster_path}")
    print(f"Extracted: {figure3c_raster}")


if __name__ == "__main__":
    main()
