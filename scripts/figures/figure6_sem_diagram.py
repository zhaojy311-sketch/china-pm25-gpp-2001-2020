from __future__ import annotations

import math
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "figure6"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE_TOP = ROOT / "data" / "review_required" / "figure6" / "Fig6_top_source.png"

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial"],
        "font.size": 9.5,
        "mathtext.fontset": "custom",
        "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold",
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "hatch.linewidth": 0.55,
    }
)

PURPLE = "#7030A0"
BLUE = "#0072BC"
RED = "#ED1C24"
GOLD = "#FDBE00"
BLACK = "#111111"
GREY = "#9B9B9B"


def arrow(ax, start, end, color=PURPLE, lw=1.35, ms=10, z=5):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=ms,
        linewidth=lw,
        color=color,
        shrinkA=0,
        shrinkB=0,
        zorder=z,
        capstyle="round",
        joinstyle="round",
    )
    ax.add_patch(patch)
    return patch


def block_arrow(ax, start, end, color=GOLD, shaft_width=.16, head_width=.48, head_length=.38, z=3):
    """Draw the straight, square-ended block arrows used in the source figure."""
    p0 = np.asarray(start, dtype=float)
    p1 = np.asarray(end, dtype=float)
    delta = p1 - p0
    length = float(np.hypot(delta[0], delta[1]))
    unit = delta / length
    normal = np.array([-unit[1], unit[0]])
    neck = p1 - unit * min(head_length, length * .42)
    pts = [
        p0 + normal * shaft_width / 2,
        neck + normal * shaft_width / 2,
        neck + normal * head_width / 2,
        p1,
        neck - normal * head_width / 2,
        neck - normal * shaft_width / 2,
        p0 - normal * shaft_width / 2,
    ]
    ax.add_patch(Polygon(pts, closed=True, facecolor=color, edgecolor="none", zorder=z))


def elbow_arrow(ax, points, color, lw=1.35, ms=10, z=4):
    xs, ys = zip(*points)
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, zorder=z, solid_capstyle="round")
    arrow(ax, points[-2], points[-1], color=color, lw=lw, ms=ms, z=z)


def slanted_text(ax, p1, p2, text, xy, color, size=10.5, boxed=False):
    a = ax.transData.transform(p1)
    b = ax.transData.transform(p2)
    angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    # Keep labels readable from left to right even when the arrow points left.
    if angle > 90:
        angle -= 180
    elif angle < -90:
        angle += 180
    ax.text(
        xy[0],
        xy[1],
        text,
        color=color,
        fontsize=size,
        rotation=angle,
        rotation_mode="anchor",
        ha="center",
        va="bottom",
        zorder=20,
        bbox=(dict(facecolor="white", edgecolor="none", alpha=.84, pad=.25) if boxed else None),
    )


def draw_sun(ax, x, y, r=0.50):
    ax.add_patch(Circle((x, y), r, facecolor="#FFF68F", edgecolor="#18315A", lw=1.0, zorder=8))
    for ang in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        u = np.array([math.cos(ang), math.sin(ang)])
        v = np.array([-math.sin(ang), math.cos(ang)])
        tip = np.array([x, y]) + u * (r + 0.45)
        b1 = np.array([x, y]) + u * (r + 0.13) + v * 0.16
        b2 = np.array([x, y]) + u * (r + 0.13) - v * 0.16
        ax.add_patch(Polygon([b1, tip, b2], closed=True, facecolor="#FFF68F", edgecolor="#18315A", lw=0.9, zorder=8))


def draw_cloud(ax, x, y, s=1.0):
    c = "#B4B1B2"
    parts = [(-0.45, 0.0, 0.44), (-0.15, 0.25, 0.50), (0.18, 0.23, 0.46), (0.48, 0.0, 0.38)]
    for dx, dy, r in parts:
        ax.add_patch(Circle((x + dx * s, y + dy * s), r * s, facecolor=c, edgecolor="none", zorder=7))
    ax.add_patch(Rectangle((x - 0.52 * s, y - 0.20 * s), 1.05 * s, 0.35 * s, facecolor=c, edgecolor="none", zorder=7))
    # PM dots inside the clouds.
    for dx, dy, rr in [(-.35,.15,.035),(-.15,.02,.045),(.05,.20,.032),(.25,.06,.035),(.36,-.08,.05),(-.02,-.10,.055)]:
        ax.add_patch(Circle((x + dx*s, y + dy*s), rr*s, facecolor="#333333", edgecolor="none", zorder=9))


def draw_rain(ax, x, y, s=1.0):
    for dx, dy in [(-.42,-.50),(-.08,-.72),(.28,-.44),(.52,-.75),(-.30,-.92),(.16,-1.03)]:
        px, py = x + dx*s, y + dy*s
        drop = Polygon(
            [(px, py + .13*s), (px - .075*s, py - .02*s), (px, py - .12*s), (px + .075*s, py - .02*s)],
            closed=True,
            facecolor="#1597D4",
            edgecolor="none",
            zorder=8,
        )
        ax.add_patch(drop)


def draw_factory(ax):
    # Factory and city silhouettes, redrawn as simple vector geometry.
    ax.add_patch(Rectangle((0.18, 0.55), 1.48, 0.56, facecolor="#303030", edgecolor="none", zorder=5))
    ax.add_patch(Polygon([(0.18,1.11),(0.46,.96),(0.68,1.18),(0.91,.99),(1.17,1.18),(1.42,.99),(1.66,1.12),(1.66,.55),(0.18,.55)], closed=True, facecolor="#303030", edgecolor="none", zorder=5))
    ax.add_patch(Polygon([(0.22,1.08),(0.28,1.92),(0.47,1.92),(0.52,1.08)], closed=True, facecolor="#303030", edgecolor="none", zorder=5))
    for wx in (0.55, 0.96, 1.36):
        ax.add_patch(Rectangle((wx, .70), .10, .14, facecolor="white", edgecolor="none", zorder=6))

    buildings = [
        (1.68,.55,.42,.92), (2.12,.55,.34,1.22), (2.49,.55,.46,1.00),
        (2.98,.55,.45,1.45), (3.45,.55,.34,1.20), (3.82,.55,.48,1.34),
    ]
    for i, (x,y,w,h) in enumerate(buildings):
        top = [(x,y),(x,y+h),(x+w*.45,y+h+.18 if i%2 else y+h),(x+w,y+h-.10),(x+w,y)]
        ax.add_patch(Polygon(top, closed=True, facecolor=GREY, edgecolor="none", zorder=4))
        for yy in np.arange(y+.25, y+h-.08, .35):
            ax.add_patch(Rectangle((x+w*.38,yy), .08,.14,facecolor="white",edgecolor="none",zorder=5))

    # Smoke from the chimney.
    for x, y, rx, ry in [(0.30,2.03,.27,.11),(.52,2.10,.36,.15),(.77,2.16,.30,.15)]:
        ax.add_patch(Ellipse((x,y),rx,ry,facecolor="#333333",edgecolor="none",zorder=6))


def draw_aerosols(ax):
    rng = np.random.default_rng(23)
    # Narrow stack plume, followed by the broad horizontal aerosol cloud in the source.
    t = np.sort(rng.uniform(0,1,62))
    plume_x = .66 + .78*t**1.35 + rng.normal(0,.08+.10*t)
    plume_y = 1.88 + 2.65*t + rng.normal(0,.10+.10*t)
    u = rng.uniform(0,1,108)
    cloud_x = 1.05 + 4.55*u + rng.normal(0,.16+.16*u)
    cloud_y = 4.30 + .34*np.sin(np.pi*u) + rng.normal(0,.23,108)
    xs = np.concatenate([plume_x,cloud_x])
    ys = np.concatenate([plume_y,cloud_y])
    radii = rng.uniform(.018,.068,len(xs))
    radii[len(plume_x):] *= rng.uniform(.95,1.35,len(cloud_x))
    shades = rng.choice(["#252525","#333333","#474747"],size=len(xs),p=[.52,.34,.14])
    for x,y,r,c in zip(xs,ys,radii,shades):
        ax.add_patch(Circle((x,y),r,facecolor=c,edgecolor="none",zorder=3,alpha=.98))
    # A few larger terminal particles as in the supplied artwork.
    for x,y,r in [(3.45,4.50,.075),(3.92,4.62,.080),(4.45,4.43,.090),(4.98,4.69,.080),(5.42,4.55,.095)]:
        ax.add_patch(Circle((x,y),r,facecolor="#303030",edgecolor="none",zorder=3))


def draw_grass(ax):
    rng = np.random.default_rng(5)
    for x in np.linspace(4.15, 16.15, 170):
        h = rng.uniform(.12, .38)
        ax.plot([x, x-rng.uniform(.03,.10)], [.55, .55+h], color="#00B83F", lw=.8, zorder=3)
        ax.plot([x, x+rng.uniform(.03,.10)], [.55, .55+h*.85], color="#00C943", lw=.7, zorder=3)
    ax.plot([.12,16.1],[.55,.55],color="#111111",lw=1.2,zorder=7)


def draw_tree(ax, x, base, scale, fill, highlight, z):
    # Brown forked trunk with a black outline, matching the original cartoon style.
    ax.plot([x, x-.03*scale], [base, base+.80*scale], color=BLACK, lw=4.2*scale, zorder=z)
    ax.plot([x, x-.03*scale], [base, base+.80*scale], color="#7B432B", lw=2.6*scale, zorder=z+.1)
    ax.plot([x-.02*scale, x-.27*scale], [base+.52*scale, base+.88*scale], color=BLACK, lw=3.3*scale, zorder=z)
    ax.plot([x-.02*scale, x-.27*scale], [base+.52*scale, base+.88*scale], color="#7B432B", lw=1.8*scale, zorder=z+.1)
    ax.plot([x-.02*scale, x+.27*scale], [base+.50*scale, base+.86*scale], color=BLACK, lw=3.3*scale, zorder=z)
    ax.plot([x-.02*scale, x+.27*scale], [base+.50*scale, base+.86*scale], color="#7B432B", lw=1.8*scale, zorder=z+.1)

    cy = base + 1.18*scale
    lobes = [(-.43,.00,.43),(-.28,.28,.43),(-.02,.40,.47),(.27,.31,.44),(.46,.04,.38),(.20,-.15,.47),(-.18,-.16,.47)]
    for dx,dy,r in lobes:
        ax.add_patch(Circle((x+dx*scale,cy+dy*scale),r*scale,facecolor=fill,edgecolor=BLACK,lw=1.65,zorder=z+1))
    # Irregular internal highlights reproduce the layered green crowns.
    for dx,dy,rx,ry in [(-.28,.22,.36,.27),(.06,.29,.43,.28),(.33,.08,.29,.23),(-.08,-.07,.46,.24)]:
        ax.add_patch(Ellipse((x+dx*scale,cy+dy*scale),rx*scale,ry*scale,facecolor=highlight,edgecolor="none",zorder=z+2,alpha=.94))


def draw_forest(ax):
    # Back row (darker, taller) and front row (brighter), closely matching the source layering.
    back = [(7.22,.94,.56),(8.18,1.00,.55),(9.18,.96,.58),(10.16,1.02,.54),
            (11.16,.95,.58),(12.12,1.00,.55),(12.92,.91,.57)]
    back_cols = [("#2E7D2A","#45A13A"),("#245E21","#3B8F34"),("#1D4E1C","#33792C")]
    for i,(x,s,base) in enumerate(back):
        fill,hi = back_cols[i%len(back_cols)]
        draw_tree(ax,x,base,s,fill,hi,4+i*.02)
    front = [(6.94,.82,.55),(7.80,.90,.56),(8.70,.84,.55),(9.58,.91,.57),
             (10.48,.85,.55),(11.37,.92,.56),(12.27,.86,.55),(13.10,.80,.56)]
    front_cols = [("#4EAA3E","#78C94C"),("#3F9635","#64B84D"),("#58B346","#7BCB50")]
    for i,(x,s,base) in enumerate(front):
        fill,hi = front_cols[i%len(front_cols)]
        draw_tree(ax,x,base,s,fill,hi,7+i*.02)

    # Seedlings at far right.
    for x in [14.55, 15.08, 15.60]:
        ax.plot([x,x],[.55,1.07],color="#6A3B17",lw=1.4,zorder=6)
        ax.add_patch(Ellipse((x-.13,.92),.31,.17,angle=30,facecolor="#75C93B",edgecolor="#39A52B",lw=.7,zorder=7))
        ax.add_patch(Ellipse((x+.13,1.03),.31,.17,angle=-30,facecolor="#75C93B",edgecolor="#39A52B",lw=.7,zorder=7))


def draw_traced_vegetation(ax):
    """Vector-trace the original forest/grass flat colours into contour paths."""
    if not SOURCE_TOP.exists():
        draw_grass(ax)
        draw_forest(ax)
        return

    src = Image.open(SOURCE_TOP).convert("RGB")
    src_w, src_h = src.size
    palette = np.array([
        [0,0,0], [108,73,44], [21,36,16], [68,133,59], [83,162,72],
        [92,179,79], [123,194,79], [123,198,84], [24,203,36], [48,210,59],
    ], dtype=float)

    def trace_crop(box, width, zbase):
        x0, y0, x1, y1 = box
        height = max(2, round(width*(y1-y0)/(x1-x0)))
        crop = src.crop(box).resize((width,height),Image.Resampling.LANCZOS)
        rgb = np.asarray(crop,dtype=float)
        r,g,b = rgb[...,0],rgb[...,1],rgb[...,2]
        eligible = ((np.maximum.reduce([r,g,b]) < 82) |
                    ((g > r*1.08) & (g > b*1.10) & (g > 38)) |
                    ((r > g*1.15) & (g > b*1.12) & (r < 185)))
        dist = ((rgb[...,None,:]-palette[None,None,:,:])**2).sum(axis=3)
        labels = dist.argmin(axis=2)
        labels[~eligible] = -1
        xs = np.linspace(x0/src_w*16.4,x1/src_w*16.4,labels.shape[1])
        ys_desc = 9.0-np.linspace(y0,y1,labels.shape[0])/src_h*8.65
        ys = ys_desc[::-1]
        for idx in range(len(palette)):
            mask = (labels==idx).astype(float)[::-1,:]
            if mask.max()==0:
                continue
            ax.contourf(xs,ys,mask,levels=[.5,1.5],colors=[tuple(palette[idx]/255.0)],
                        antialiased=True,corner_mask=True,zorder=zbase+idx*.08)

    # The first crop contains only the original forest; the second recovers the
    # original grass, exposed roots and seedlings without importing labels.
    trace_crop((685,748,1450,1048),383,4)
    trace_crop((480,952,1700,1048),610,4.9)
    # Clean vector leaves reinforce the small seedling row at the far right.
    seed_x = [14.42,14.76,15.10,15.45,15.80]
    seed_h = [.43,.50,.46,.52,.47]
    for i,(x,h) in enumerate(zip(seed_x,seed_h)):
        ax.plot([x,x],[.56,.56+h],color="#7A3F16",lw=1.0,zorder=9)
        ax.add_patch(Ellipse((x-.10,.56+h-.10),.25,.13,angle=28,facecolor="#72C837",edgecolor="#45AE2D",lw=.45,zorder=10))
        ax.add_patch(Ellipse((x+.10,.56+h-.02),.25,.13,angle=-28,facecolor="#72C837",edgecolor="#45AE2D",lw=.45,zorder=10))
        if i%2:
            ax.add_patch(Ellipse((x-.03,.56+h+.08),.20,.11,angle=78,facecolor="#82D142",edgecolor="#45AE2D",lw=.4,zorder=10))
    ax.plot([.12,16.1],[.55,.55],color="#111111",lw=1.2,zorder=12)


def draw_top(ax, panel_label=None):
    ax.set_xlim(0, 16.4)
    ax.set_ylim(0.35, 9.0)
    ax.set_aspect("equal")
    ax.axis("off")

    # Landscape layer.
    draw_factory(ax)
    draw_aerosols(ax)
    draw_traced_vegetation(ax)

    # Sun/PAR.
    draw_sun(ax, 2.18, 7.72, .50)
    ax.text(2.90, 7.18, "PAR", fontsize=13, fontweight="bold", color=BLACK, ha="left", va="center")
    ax.text(2.30, 6.82, r"(PAR=PAR$_{dir}$+PAR$_{dif}$)", fontsize=8.6, fontweight="bold", color=BLACK, ha="left")

    # Clouds, rain, and precipitation label.
    draw_cloud(ax, 13.55, 8.10, .95)
    draw_cloud(ax, 15.05, 8.10, .95)
    draw_rain(ax, 13.55, 7.85, .95)
    draw_rain(ax, 15.05, 7.85, .95)
    ax.text(14.30, 6.98, "Pre", fontsize=13, fontweight="bold", ha="center", va="center")

    # Gold radiative arrows and labels (square shafts and triangular heads as in the source).
    block_arrow(ax,(3.45,6.42),(5.28,4.48),shaft_width=.24,head_width=.66,head_length=.48,z=2)
    slanted_text(ax,(3.45,6.42),(5.28,4.48),"Direct radiation",(4.48,5.48),BLACK,11)
    block_arrow(ax,(5.82,4.18),(7.72,2.58),shaft_width=.23,head_width=.65,head_length=.47,z=2)
    # Diffuse-radiation arrows around the canopy.
    for a,b in [((5.45,2.18),(6.03,1.88)),((5.40,1.22),(5.98,1.50)),((7.22,2.73),(7.50,2.17)),
                ((8.92,2.76),(9.18,2.16)),((11.72,2.72),(11.48,2.10)),((14.25,2.12),(13.70,1.82)),
                ((14.35,1.46),(13.73,1.46)),((14.12,.98),(13.56,1.26))]:
        block_arrow(ax,a,b,shaft_width=.075,head_width=.27,head_length=.22,z=11)
    ax.text(5.20,1.72,"Diffuse\nradiation",fontsize=10.5,ha="center",va="top",color=BLACK,zorder=20)

    # Variable labels.
    ax.text(6.55,5.08,r"PM$_{2.5}$",fontsize=13,fontweight="bold",ha="center",va="center")
    ax.text(9.90,7.18,r"T$_a$",fontsize=13,fontweight="bold",ha="center",va="center")
    ax.text(12.85,5.12,"RH",fontsize=13,fontweight="bold",ha="center",va="center")
    ax.text(12.00,3.93,"VPD",fontsize=13,fontweight="bold",ha="center",va="center")
    ax.text(7.92,4.02,r"V$_{cmax}$",fontsize=12.5,fontweight="bold",ha="center",va="center")
    ax.text(9.82,2.95,"GPP",fontsize=13,fontweight="bold",ha="center",va="center")
    ax.text(4.20,2.10,"NTL",fontsize=12,fontweight="bold",ha="center",va="center")
    ax.text(14.85,2.10,"LAI",fontsize=12,fontweight="bold",ha="center",va="center")
    ax.text(2.20,3.55,"Aerosols",fontsize=10.8,ha="center",va="center",zorder=20)

    # Purple SEM arrows.
    purple_paths = [
        ((6.20,5.42),(4.55,6.85)), ((6.90,5.45),(9.45,7.05)),
        ((6.85,4.85),(7.63,4.25)), ((7.05,5.34),(13.58,7.12)),
        ((9.90,6.80),(9.84,3.33)), ((10.40,6.88),(11.82,4.27)),
        ((14.05,6.67),(13.05,5.37)), ((12.64,4.84),(12.15,4.25)),
        ((11.70,3.77),(10.23,3.11)), ((8.26,3.80),(9.50,3.10)),
    ]
    for p1,p2 in purple_paths:
        arrow(ax,p1,p2,color=PURPLE,lw=1.35,ms=9,z=10)

    # Path coefficients.
    slanted_text(ax,(6.20,5.42),(4.55,6.85),"-0.03***",(5.42,6.18),BLUE,10.5)
    slanted_text(ax,(6.90,5.45),(9.45,7.05),"-0.13***",(8.05,6.30),BLUE,10.5)
    slanted_text(ax,(6.85,4.85),(7.63,4.25),"-0.14***",(7.40,4.78),BLUE,10.5)
    slanted_text(ax,(7.05,5.34),(13.58,7.12),"0.18***",(12.03,6.76),RED,10.5)
    ax.text(10.03,5.42,"0.24***",color=RED,fontsize=10.5,ha="left",va="center")
    slanted_text(ax,(10.40,6.88),(11.82,4.27),"0.83***",(11.12,5.58),RED,10.5)
    slanted_text(ax,(14.05,6.67),(13.05,5.37),"0.80***",(13.56,5.96),RED,10.5)
    ax.text(12.62,4.55,"-0.46***",color=BLUE,fontsize=10.5,ha="left",va="bottom",zorder=20)
    slanted_text(ax,(11.70,3.77),(10.23,3.11),"-0.14***",(11.18,3.53),BLUE,10.5)
    slanted_text(ax,(8.26,3.80),(9.50,3.10),"0.25***",(8.92,3.45),RED,10.5)

    # Direct environmental effects on GPP.
    elbow_arrow(ax,[(3.42,6.55),(3.42,2.95),(9.44,2.95)],RED,lw=1.35,ms=9,z=6)
    ax.text(3.80,3.13,"0.01***",color=RED,fontsize=10.5,ha="left",va="bottom")
    elbow_arrow(ax,[(14.30,6.70),(14.30,2.95),(10.30,2.95)],RED,lw=1.35,ms=9,z=6)
    ax.text(14.34,4.70,"0.12***",color=RED,fontsize=10.5,ha="left",va="center")
    arrow(ax,(4.55,2.02),(9.48,2.72),color=BLUE,lw=1.35,ms=9,z=11)
    slanted_text(ax,(4.55,2.02),(9.48,2.72),"-0.01***",(6.05,2.39),BLUE,10.5)
    arrow(ax,(14.45,2.02),(10.30,2.73),color=RED,lw=1.35,ms=9,z=11)
    slanted_text(ax,(14.45,2.02),(10.30,2.73),"0.56***",(12.62,2.57),RED,10.5,boxed=True)

    if panel_label:
        ax.text(.01,.98,panel_label,transform=ax.transAxes,fontsize=13,fontweight="bold",ha="left",va="top")


def draw_bottom(label_ax, bar_ax, panel_label=None):
    y_direct = [10.2, 9.15, 8.10]
    y_dnet = 6.95
    y_indirect = [4.60, 3.55, 2.50]
    y_inet = 1.35
    y_total = -0.55
    ylim = (-1.55, 11.25)

    label_ax.set_xlim(0,1)
    label_ax.set_ylim(*ylim)
    label_ax.axis("off")

    direct_labels = [
        r"PM$_{2.5}$-T$_a$-GPP",
        r"PM$_{2.5}$-V$_{cmax}$-GPP",
        r"PM$_{2.5}$-PAR-GPP",
    ]
    indirect_labels = [
        r"PM$_{2.5}$-T$_a$-VPD-GPP",
        r"PM$_{2.5}$-Pre-RH-VPD-GPP",
        r"PM$_{2.5}$-Pre-GPP",
    ]
    for y, txt in zip(y_direct, direct_labels):
        label_ax.text(.96,y,txt,ha="right",va="center",fontsize=10,color="#4472C4")
    label_ax.text(.96,y_dnet,"Direct net effect",ha="right",va="center",fontsize=10,color="#4472C4",fontweight="bold")
    for y, txt in zip(y_indirect, indirect_labels):
        label_ax.text(.96,y,txt,ha="right",va="center",fontsize=10,color="#C00000")
    label_ax.text(.96,y_inet,"Indirect net effect",ha="right",va="center",fontsize=10,color="#C00000",fontweight="bold")
    label_ax.text(.96,y_total,"Total effect",ha="right",va="center",fontsize=10,color=BLACK,fontweight="bold")
    if panel_label:
        label_ax.text(.02,.98,panel_label,transform=label_ax.transAxes,fontsize=13,fontweight="bold",ha="left",va="top")

    bar_ax.set_xlim(-.095,.060)
    bar_ax.set_ylim(*ylim)
    bar_ax.set_yticks([])
    for side in ["left","right","top"]:
        bar_ax.spines[side].set_visible(False)
    bar_ax.spines["bottom"].set_position(("data",-1.18))
    bar_ax.spines["bottom"].set_linewidth(1.0)
    # Keep the zero line behind the bars so the accurate -0.0003 bar remains visible.
    bar_ax.axvline(0,color=BLACK,lw=1.0,zorder=1)
    ticks = [-.09,-.07,-.05,-.03,-.01,.01,.03,.05]
    bar_ax.set_xticks(ticks)
    bar_ax.set_xticklabels([f"{v:.2f}" for v in ticks],fontsize=8.8)
    bar_ax.tick_params(axis="x",length=4,width=1,direction="inout",pad=4)

    direct_vals = [-.0312,-.0364,-.0003]
    direct_colors = ["#4472C4","#A9C7E6","#7F9ACB"]
    indirect_vals = [.0151,.0102,.0216]
    indirect_colors = ["#C00000","#F1A875","#C85A0A"]
    h = .72
    for y,v,c in zip(y_direct,direct_vals,direct_colors):
        bar_ax.barh(y,v,height=h,color=c,edgecolor=c,linewidth=.65,zorder=5)
        # Label just outside the negative end; tiny PAR effect is labelled left of zero.
        x = v-.0022 if abs(v)>.004 else -.0022
        bar_ax.text(x,y,f"{v:.4f}",ha="right",va="center",fontsize=9.5,color=BLACK,zorder=12)
    bar_ax.barh(y_dnet,-.0679,height=h,facecolor="white",edgecolor="#4472C4",hatch="////////",linewidth=.6,zorder=3)
    bar_ax.text(-.0702,y_dnet,"-0.0679",ha="right",va="center",fontsize=9.5)

    for y,v,c in zip(y_indirect,indirect_vals,indirect_colors):
        bar_ax.barh(y,v,height=h,color=c,edgecolor="none",zorder=3)
        bar_ax.text(v+.0022,y,f"{v:.4f}",ha="left",va="center",fontsize=9.5)
    bar_ax.barh(y_inet,.0469,height=h,facecolor="white",edgecolor="#C00000",hatch="////////",linewidth=.6,zorder=3)
    bar_ax.text(.0490,y_inet,"0.0469",ha="left",va="center",fontsize=9.5)
    bar_ax.barh(y_total,-.021,height=h,color="#D1D1D1",edgecolor="none",zorder=3)
    bar_ax.text(-.0232,y_total,"-0.021",ha="right",va="center",fontsize=9.5)

    # Directional caption below x-axis.
    bar_ax.text(.10,-.17,"Inhibitory",transform=bar_ax.transAxes,ha="center",va="center",fontsize=10,clip_on=False)
    bar_ax.annotate("",xy=(.21,-.17),xytext=(.36,-.17),xycoords="axes fraction",textcoords="axes fraction",arrowprops=dict(arrowstyle="-|>",color=BLACK,lw=1.0),annotation_clip=False)
    bar_ax.text(.50,-.17,"Path effect",transform=bar_ax.transAxes,ha="center",va="center",fontsize=10,fontweight="bold",clip_on=False)
    bar_ax.annotate("",xy=(.79,-.17),xytext=(.64,-.17),xycoords="axes fraction",textcoords="axes fraction",arrowprops=dict(arrowstyle="-|>",color=BLACK,lw=1.0),annotation_clip=False)
    bar_ax.text(.90,-.17,"Promoting",transform=bar_ax.transAxes,ha="center",va="center",fontsize=10,clip_on=False)


def save_all(fig, stem):
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", facecolor="white")


def make_top():
    fig = plt.figure(figsize=(7.09,4.15),facecolor="white")
    ax = fig.add_axes([.015,.02,.97,.96])
    draw_top(ax)
    save_all(fig,"Fig6a_路径示意图")
    plt.close(fig)


def make_bottom():
    fig = plt.figure(figsize=(7.09,4.05),facecolor="white")
    label_ax = fig.add_axes([.02,.14,.34,.82])
    bar_ax = fig.add_axes([.36,.14,.61,.82])
    draw_bottom(label_ax,bar_ax)
    save_all(fig,"Fig6b_路径效应图")
    plt.close(fig)


def make_combined():
    fig = plt.figure(figsize=(7.09,8.25),facecolor="white")
    top_ax = fig.add_axes([.015,.515,.97,.475])
    label_ax = fig.add_axes([.02,.075,.34,.395])
    bar_ax = fig.add_axes([.36,.075,.61,.395])
    draw_top(top_ax,panel_label="a")
    draw_bottom(label_ax,bar_ax,panel_label="b")
    save_all(fig,"Fig6_组合图")
    plt.close(fig)


if __name__ == "__main__":
    # Render the largest figure first to keep peak raster memory predictable.
    make_combined()
    make_top()
    make_bottom()
    note = """Fig. 6 vector redraw notes

Outputs are fully redrawn vector artwork; the original raster images are not embedded.

Reconstructed path-effect values:
Direct: PM2.5-Ta-GPP = -0.0312 (inferred), PM2.5-Vcmax-GPP = -0.0364,
PM2.5-PAR-GPP = -0.0003; direct net effect = -0.0679.
Indirect: 0.0151, 0.0102, 0.0216; indirect net effect = 0.0469.
Total effect = -0.021.

Important: -0.0312 was not legible as a printed value in the supplied raster image.
It was inferred from -0.0679 - (-0.0364) - (-0.0003) and should be checked
against the manuscript or original analysis before submission.

All figure text uses embedded Arial (regular, bold, or italic by role).
The vegetation was colour-region traced into vector paths; no source raster is embedded.
SVG retains editable text. PDF uses TrueType font embedding. PNG/TIFF are 600 dpi.
"""
    (OUT / "README_数值与输出说明.txt").write_text(note,encoding="utf-8")
    print(f"Saved outputs to: {OUT}")
