#!/usr/bin/env Rscript

# Regional small-multiple plot for weighted SHAP contributions (2001-2020).
# Locator rectangles reproduce the approximate regional positions shown in the
# source figure; they are schematic zones, not administrative boundaries.

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(scales)
  library(sf)
})

args <- commandArgs(trailingOnly = TRUE)
script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
script_dir <- if (length(script_arg)) dirname(normalizePath(sub("^--file=", "", script_arg[1]), mustWork = TRUE)) else getwd()
repo_dir <- normalizePath(file.path(script_dir, "..", ".."), mustWork = TRUE)
output_dir <- if (length(args) >= 1) args[1] else file.path(repo_dir, "outputs", "figure3b")
input_csv <- if (length(args) >= 2) args[2] else file.path(
  repo_dir, "data", "review_required", "figure3",
  "SHAP_weighted_contributions_2001_2020.csv"
)
geojson_candidates <- c(
  if (length(args) >= 3) args[3] else NA_character_,
  file.path(repo_dir, "data", "review_required", "boundaries", "china_provinces", "china_provinces.geojson")
)
geojson_candidates <- geojson_candidates[!is.na(geojson_candidates)]
input_geojson <- geojson_candidates[file.exists(geojson_candidates)][1]
if (is.na(input_geojson)) {
  stop("China provincial GeoJSON not found. Pass its path as the third argument.")
}
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

font_family <- "Arial"
# 与上一张图按相同版面宽度排版时，所有可见文字采用同一字号。
# 16 pt 在当前 8.5 in 宽的画布上与上一张图的相对字高接近，同时
# 能在移除柱端数值后保持足够大的阅读尺寸。
font_size <- 15

# Require the requested typeface so every text element is genuinely Arial.
available_fonts <- unique(systemfonts::system_fonts()$family)
if (!any(tolower(available_fonts) == tolower(font_family))) {
  stop("Arial is not installed. Install Arial before rendering this figure.")
}
theme_set(theme_gray(base_family = font_family))
regions <- c("NW", "FW", "NE", "SWC", "NC", "CSC", "SC", "EC")
factors <- c("LAI", "Ta", "Pre", "PM2.5", "RH", "VPD", "PAR", "NTL")
factor_labeler <- function(x) {
  # Plotmath keeps the PM2.5 subscript portable in PNG, PDF, and SVG.
  as.expression(lapply(x, function(label) {
    if (label == "PM2.5") bquote(PM[2.5]) else label
  }))
}

region_palette <- c(
  "NW" = "#3C78A8", "FW" = "#D95F59", "NE" = "#2A8C68",
  "SWC" = "#C49A27", "NC" = "#36A6C9", "CSC" = "#A64883",
  "SC" = "#7A7A7A", "EC" = "#51459B"
)

# Approximate bounding boxes read from the source figure's central locator map.
# These boxes are intentionally labelled as schematic in the figure caption.
region_boxes <- data.frame(
  Region = regions,
  xmin = c(82,  99, 120, 82, 109, 101, 103, 112),
  xmax = c(101, 109, 134, 101, 121, 112, 115, 123),
  ymin = c(34,  35,  41, 22,  34,  24,  18,  25),
  ymax = c(43,  44,  53, 34,  43,  34,  25,  34)
)

wide <- read.csv(input_csv, check.names = FALSE, stringsAsFactors = FALSE)
stopifnot(all(c("Region", factors) %in% names(wide)))
wide <- wide[match(regions, wide$Region), c("Region", factors)]

long <- data.frame(
  Region = rep(wide$Region, each = length(factors)),
  Factor = rep(factors, times = nrow(wide)),
  Contribution = as.vector(t(as.matrix(wide[, factors]))),
  stringsAsFactors = FALSE
)
long$Factor <- factor(long$Factor, levels = rev(factors))
long$Region <- factor(long$Region, levels = regions)

# Read GeoJSON from text rather than handing its filesystem path to GDAL.
# This is robust to Windows installations where GDAL/R cannot decode Chinese
# directory names under the active locale.
geojson_text <- paste(
  readLines(input_geojson, warn = FALSE, encoding = "UTF-8"),
  collapse = "\n"
)
china_map <- st_read(geojson_text, quiet = TRUE)
china_map <- st_transform(china_map, 4326)
geometry_types <- as.character(st_geometry_type(china_map))
china_polygons <- china_map[geometry_types %in% c("POLYGON", "MULTIPOLYGON"), ]
china_lines <- china_map[geometry_types %in% c("LINESTRING", "MULTILINESTRING"), ]

make_locator <- function(region_code, region_colour) {
  box <- region_boxes[region_boxes$Region == region_code, , drop = FALSE]

  main_map <- ggplot() +
    geom_sf(
      data = china_polygons, fill = "#F1F3F5",
      colour = "#7F8790", linewidth = 0.16
    ) +
    geom_sf(data = china_lines, colour = "#7F8790", linewidth = 0.18) +
    geom_rect(
      data = box, inherit.aes = FALSE,
      aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax),
      fill = alpha(region_colour, 0.32), colour = region_colour,
      linewidth = 0.65
    ) +
    coord_sf(
      xlim = c(73, 140), ylim = c(18, 54),
      expand = FALSE, datum = NA
    ) +
    theme_void(base_family = font_family) +
    theme(
      panel.background = element_rect(fill = "white", colour = "#B5BBC2", linewidth = 0.35),
      plot.background = element_rect(fill = "white", colour = NA),
      plot.margin = margin(1.5, 1.5, 1.5, 1.5)
    )

  south_china_sea <- ggplot() +
    geom_sf(
      data = china_polygons, fill = "#F1F3F5",
      colour = "#7F8790", linewidth = 0.15
    ) +
    geom_sf(data = china_lines, colour = "#7F8790", linewidth = 0.20) +
    coord_sf(
      xlim = c(105, 125), ylim = c(3, 25),
      expand = FALSE, datum = NA
    ) +
    theme_void(base_family = font_family) +
    theme(
      panel.border = element_rect(
        fill = NA, colour = "#A7ADB4", linewidth = 0.35
      ),
      panel.background = element_rect(fill = "white", colour = NA),
      plot.background = element_rect(fill = "white", colour = NA),
      plot.margin = margin(0, 0, 0, 0)
    )

  main_map + inset_element(
    south_china_sea,
    left = 0.79, bottom = 0.025, right = 0.985, top = 0.46,
    align_to = "panel", on_top = TRUE
  )
}

make_panel <- function(region_code, show_x_title = FALSE) {
  dat <- long[long$Region == region_code, , drop = FALSE]
  colour <- region_palette[[region_code]]
  locator_grob <- patchworkGrob(make_locator(region_code, colour))

  ggplot(dat, aes(x = Contribution, y = Factor)) +
    geom_col(
      width = 0.56, fill = colour, colour = darken(colour, 0.12),
      linewidth = 0.25
    ) +
    # 地区标签放在面板框线内右上角。使用 panel 坐标定位，使八个面板
    # 的标签位置完全一致，并在离散纵轴上方预留空白，避免覆盖最长柱。
    annotation_custom(
      grid::textGrob(
        region_code,
        x = grid::unit(1, "npc") - grid::unit(1.8, "mm"),
        y = grid::unit(1, "npc") - grid::unit(1.5, "mm"),
        just = c("right", "top"),
        gp = grid::gpar(
          fontfamily = font_family, fontsize = font_size,
          fontface = "bold", col = colour
        )
      ),
      xmin = -Inf, xmax = Inf, ymin = -Inf, ymax = Inf
    ) +
    # 柱端数值已移除；释放出的空间用于放大区域定位图和全部文字。
    annotation_custom(locator_grob, xmin = 38.0, xmax = 65.0, ymin = 0.25, ymax = 5.55) +
    scale_y_discrete(
      labels = factor_labeler, drop = FALSE,
      expand = expansion(add = c(0.52, 1.28))
    ) +
    scale_x_continuous(
      limits = c(0, 65), breaks = c(0, 20, 40, 60),
      minor_breaks = c(10, 30, 50), expand = expansion(mult = c(0, 0))
    ) +
    coord_cartesian(clip = "off") +
    labs(
      title = NULL,
      x = if (show_x_title) "Relative contribution (%)" else NULL,
      y = NULL
    ) +
    theme_classic(base_size = font_size, base_family = font_family) +
    theme(
      text = element_text(family = font_family, size = font_size),
      axis.title = element_text(
        family = font_family, size = font_size, colour = "#1F1F1F"
      ),
      axis.title.x = element_text(margin = margin(t = 2)),
      axis.title.y = element_text(margin = margin(r = 2)),
      axis.text.x = element_text(
        family = font_family, size = font_size, colour = "#333333"
      ),
      axis.text.y = element_text(
        family = font_family, size = font_size, colour = "#202124"
      ),
      axis.ticks = element_line(linewidth = 0.28, colour = "#333333"),
      axis.ticks.length = unit(0.5, "mm"),
      axis.line = element_blank(),
      panel.border = element_rect(
        colour = "#333333", fill = NA, linewidth = 0.28
      ),
      panel.grid.major.x = element_line(linewidth = 0.25, colour = "#D8DCE1"),
      panel.grid.minor.x = element_line(linewidth = 0.18, colour = "#EEF0F2"),
      panel.grid.major.y = element_blank(),
      plot.margin = margin(1.5, 3.5, 2, 2.5)
    )
}

# colorspace::darken is available through the colorspace dependency of ggplot2.
darken <- function(colour, amount = 0.12) colorspace::darken(colour, amount)

plots <- lapply(seq_along(regions), function(i) {
  make_panel(
    regions[i],
    show_x_title = i >= 7
  )
})

combined <- wrap_plots(plots, ncol = 2, byrow = TRUE) +
  plot_layout(heights = rep(1, 4))

ggsave(
  file.path(output_dir, "SHAP_regional_facets_locator_R.png"), combined,
  device = ragg::agg_png, width = 8.5, height = 10.4, units = "in",
  dpi = 600, background = "white"
)
ggsave(
  file.path(output_dir, "SHAP_regional_facets_locator_R.pdf"), combined,
  device = cairo_pdf, width = 8.5, height = 10.4, units = "in",
  bg = "white"
)
ggsave(
  file.path(output_dir, "SHAP_regional_facets_locator_R.svg"), combined,
  device = svglite::svglite, width = 8.5, height = 10.4, units = "in",
  bg = "white"
)
ggsave(
  file.path(output_dir, "SHAP_regional_facets_locator_R.tif"), combined,
  device = ragg::agg_tiff, width = 8.5, height = 10.4, units = "in",
  dpi = 600, compression = "lzw", background = "white"
)

message("Created PNG, PDF, SVG, and 600 dpi TIFF outputs.")
