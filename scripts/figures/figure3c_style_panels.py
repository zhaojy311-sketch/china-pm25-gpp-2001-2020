from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "review_required" / "figure3" / "Figure3c_Arial_article_style.svg"
OUTPUT = ROOT / "outputs" / "figure3c" / "SHAP_dependence_unified.svg"

FONT_SIZE = 54
SUPERSCRIPT_SIZE = round(FONT_SIZE * 0.66, 2)
FRAME_COLOR = "#333333"
FRAME_WIDTH = 2.5
TICK_LENGTH = 5


PLOTS = (
    # left, top, right, bottom, x ticks, y ticks
    (330, 51, 980, 696, (330, 546.667, 763.333, 980), (51, 180, 309, 438, 567, 696)),
    (1393, 51, 2044, 696, (1393, 1718.5, 2044), (51, 212.25, 373.5, 534.75, 696)),
    (2431, 51, 3082, 696, (2431, 2648, 2865, 3082), (51, 266, 481, 696)),
    (3509, 51, 4158, 696, (3509, 3639, 3769, 3899, 4029, 4158), (51, 212.25, 373.5, 534.75, 696)),
    (330, 938, 980, 1584, (330, 492.5, 655, 817.5, 980), (938, 1153.333, 1368.667, 1584)),
    (1393, 938, 2044, 1584, (1393, 1718.5, 2044), (938, 1099.5, 1261, 1422.5, 1584)),
    (2428, 938, 3078, 1584, (2428, 2567.286, 2706.571, 2845.857, 3078), (938, 1153.333, 1368.667, 1584)),
    (3508, 938, 4158, 1584, (3508, 3724.667, 3941.333, 4158), (938, 1099.5, 1261, 1422.5, 1584)),
)


def frame_overlay() -> str:
    elements: list[str] = [
        '<g id="unified-axes" fill="none" '
        f'stroke="{FRAME_COLOR}" stroke-width="{FRAME_WIDTH}" '
        'shape-rendering="geometricPrecision">'
    ]
    for left, top, right, bottom, x_ticks, y_ticks in PLOTS:
        elements.append(
            f'<rect x="{left}" y="{top}" width="{right-left}" '
            f'height="{bottom-top}"/>'
        )
        for x in x_ticks:
            elements.append(
                f'<line x1="{x}" y1="{bottom}" x2="{x}" '
                f'y2="{bottom + TICK_LENGTH}"/>'
            )
        for y in y_ticks:
            elements.append(
                f'<line x1="{left - TICK_LENGTH}" y1="{y}" '
                f'x2="{left}" y2="{y}"/>'
            )
    elements.append("</g>")
    return "".join(elements)


def main() -> None:
    svg = SOURCE.read_text(encoding="utf-8")

    # Every ordinary label uses one size.  Scientific exponents and chemical
    # subscripts remain proportionally smaller by typographic convention.
    svg = re.sub(r'font-size="(?:70|66|62)"', f'font-size="{FONT_SIZE}"', svg)
    svg = re.sub(
        r'font-size="(?:46\.2|43\.56)"',
        f'font-size="{SUPERSCRIPT_SIZE}"',
        svg,
    )
    svg = svg.replace('fill="#595959"', 'fill="#000000"')
    svg = svg.replace("</svg>", frame_overlay() + "</svg>")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()
