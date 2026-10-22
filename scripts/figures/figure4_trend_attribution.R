#!/usr/bin/env Rscript

# Reproduce Figure 4 from the two source workbooks with a unified journal style.
# Source values are not modified. The script exports 600-dpi PNG/TIFF and a
# vector PDF using Arial throughout.

suppressPackageStartupMessages({
  library(readxl)
  library(ggplot2)
  library(patchwork)
  library(dplyr)
  library(scales)
})

script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
script_dir <- if (length(script_arg)) dirname(normalizePath(sub("^--file=", "", script_arg[1]), mustWork = TRUE)) else getwd()
repo_dir <- normalizePath(file.path(script_dir, "..", ".."), mustWork = TRUE)
data_dir <- file.path(repo_dir, "data", "review_required", "figure4")
main_file <- file.path(data_dir, "Figure4_relative_contributions.xlsx")
inset_file <- file.path(data_dir, "Figure4_GPP_insets.xlsx")
output_dir <- file.path(repo_dir, "outputs", "figure4")

args <- commandArgs(trailingOnly = TRUE)
for (arg in args) {
  if (grepl("^--main=", arg)) main_file <- sub("^--main=", "", arg)
  if (grepl("^--inset=", arg)) inset_file <- sub("^--inset=", "", arg)
  if (grepl("^--outdir=", arg)) output_dir <- sub("^--outdir=", "", arg)
}

stopifnot(file.exists(main_file), file.exists(inset_file))
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

font_family <- "Arial"
period_1 <- "2001–2013"
period_2 <- "2013–2020"
color_1 <- "#A0A0A4"
color_2 <- "#48C6EB"
text_color <- "#202124"
region_order <- c("FW", "NE", "NW", "NC", "SWC", "EC", "CSC", "SC")
period_colors <- setNames(c(color_1, color_2), c(period_1, period_2))
error_colors <- setNames(c("#88888C", "#00AFEF"), c(period_1, period_2))

# Directions transcribed from the supplied Figure 4 sample. The first sign is
# for 2001–2013 and the second for 2013–2020. NA means absent/zero contribution.
directions <- list(
  FW = list(LAI = c(1, 1), RH = c(-1, NA), NTL = c(1, NA), `PM2.5` = c(1, -1)),
  NE = list(LAI = c(1, 1), Ta = c(NA, 1), Pre = c(1, NA), RH = c(NA, -1),
            VPD = c(NA, 1), NTL = c(1, -1), `PM2.5` = c(1, -1)),
  NW = list(LAI = c(1, 1), NTL = c(1, NA), `PM2.5` = c(1, -1)),
  NC = list(LAI = c(1, 1), Pre = c(1, NA), NTL = c(1, NA), `PM2.5` = c(1, -1)),
  SWC = list(LAI = c(1, 1), RH = c(-1, 1), VPD = c(1, NA), PAR = c(NA, -1),
             NTL = c(1, 1), `PM2.5` = c(1, -1)),
  EC = list(LAI = c(1, 1), Ta = c(NA, 1), RH = c(-1, NA), NTL = c(1, NA),
            `PM2.5` = c(1, -1)),
  CSC = list(LAI = c(1, 1), NTL = c(1, NA), RH = c(-1, NA), VPD = c(1, NA),
             `PM2.5` = c(1, -1)),
  SC = list(LAI = c(1, 1), NTL = c(1, NA), `PM2.5` = c(1, -1))
)

arrow_symbol <- function(x) {
  if (is.na(x)) return(NA_character_)
  if (x > 0) "↑" else "↓"
}

read_contribution <- function(region) {
  raw <- read_excel(main_file, sheet = region, col_names = TRUE)
  stopifnot(ncol(raw) >= 5)
  raw <- raw[, 1:5]
  names(raw) <- c("variable", "value_1", "error_1", "value_2", "error_2")
  raw %>%
    mutate(
      variable = trimws(as.character(variable)),
      across(c(value_1, error_1, value_2, error_2), as.numeric),
      # Every panel uses the same seven-slot horizontal scale. This keeps the
      # physical bar width identical even when a region has fewer variables.
      x = if (n() == 1) 4 else seq(1, 7, length.out = n())
    )
}

read_gpp <- function(region) {
  raw <- read_excel(inset_file, sheet = region, col_names = TRUE)
  stopifnot(ncol(raw) >= 2)
  raw <- raw[, 1:2]
  names(raw) <- c("year", "gpp")
  raw %>%
    transmute(year = as.numeric(year), gpp = as.numeric(gpp)) %>%
    filter(is.finite(year), is.finite(gpp)) %>%
    arrange(year)
}

build_inset <- function(region) {
  raw <- read_gpp(region)
  segmented <- bind_rows(
    raw %>% filter(year <= 2013) %>% mutate(period = period_1),
    raw %>% filter(year >= 2013) %>% mutate(period = period_2)
  ) %>% mutate(period = factor(period, levels = c(period_1, period_2)))

  ggplot(segmented, aes(year, gpp, color = period)) +
    geom_smooth(method = "lm", formula = y ~ x, se = FALSE, linewidth = 0.55, fullrange = FALSE) +
    geom_point(shape = 21, fill = "white", stroke = 0.55, size = 1.25) +
    scale_color_manual(values = period_colors, drop = FALSE) +
    scale_x_continuous(breaks = c(2001, 2013, 2020), limits = c(2000.3, 2020.7), expand = c(0, 0)) +
    scale_y_continuous(breaks = breaks_pretty(n = 3), labels = label_number(accuracy = 1)) +
    guides(color = "none") +
    labs(x = NULL, y = NULL) +
    theme_classic(base_family = font_family, base_size = 7.6) +
    theme(
      axis.line = element_line(color = "#555555", linewidth = 0.28),
      axis.ticks = element_line(color = "#555555", linewidth = 0.28),
      axis.ticks.length = grid::unit(1.2, "pt"),
      axis.text = element_text(color = text_color, size = 7.4, margin = margin(0.7, 0.7, 0.7, 0.7)),
      plot.background = element_rect(fill = "white", color = NA),
      panel.background = element_rect(fill = "white", color = NA),
      plot.margin = margin(1, 1, 1, 1, unit = "pt")
    )
}

build_panel <- function(region) {
  raw <- read_contribution(region)
  panel_letter <- letters[match(region, region_order)]
  bars <- bind_rows(
    raw %>% transmute(x, variable, period = period_1, value = coalesce(value_1, 0), error = coalesce(error_1, 0)),
    raw %>% transmute(x, variable, period = period_2, value = coalesce(value_2, 0), error = coalesce(error_2, 0))
  ) %>%
    mutate(
      period = factor(period, levels = c(period_1, period_2)),
      ymin = pmax(0, value - error),
      ymax = value + error
    )

  label_data <- raw %>%
    mutate(
      before = vapply(variable, function(v) arrow_symbol(directions[[region]][[v]][1]), character(1)),
      after = vapply(variable, function(v) arrow_symbol(directions[[region]][[v]][2]), character(1)),
      offset = 0.050 * nchar(variable) + 0.065
    )
  dodge <- position_dodge(width = 0.62)
  main_plot <- ggplot(bars, aes(x, value, fill = period)) +
    geom_col(position = dodge, width = 0.58, color = "#474747", linewidth = 0.30) +
    geom_errorbar(
      aes(ymin = ymin, ymax = ymax, color = period),
      position = dodge, width = 0.13, linewidth = 0.38
    ) +
    geom_hline(yintercept = 0, color = "#606060", linewidth = 0.42) +
    geom_segment(
      data = raw, aes(x = x, xend = x, y = 0, yend = -0.014),
      inherit.aes = FALSE, color = "#606060", linewidth = 0.42
    ) +
    geom_text(
      data = label_data, aes(x = x, y = -0.050, label = variable),
      inherit.aes = FALSE, family = font_family, size = 3.20,
      color = text_color, vjust = 0.5
    ) +
    geom_text(
      data = filter(label_data, !is.na(before)),
      aes(x = x - offset, y = -0.050, label = before),
      inherit.aes = FALSE, family = font_family, fontface = "bold",
      size = 4.00, color = color_1, vjust = 0.5
    ) +
    geom_text(
      data = filter(label_data, !is.na(after)),
      aes(x = x + offset, y = -0.050, label = after),
      inherit.aes = FALSE, family = font_family, fontface = "bold",
      size = 4.00, color = color_2, vjust = 0.5
    ) +
    annotate(
      "text", x = -Inf, y = Inf, label = paste0("(", panel_letter, ") ", region),
      hjust = -0.10, vjust = 1.18, family = font_family, fontface = "bold",
      size = 4.05, color = text_color
    ) +
    scale_fill_manual(values = period_colors, drop = FALSE) +
    scale_color_manual(values = error_colors, drop = FALSE) +
    scale_x_continuous(
      limits = c(0.35, 7.65), breaks = NULL,
      expand = c(0, 0)
    ) +
    scale_y_continuous(
      breaks = seq(0, 1, 0.25),
      labels = label_percent(accuracy = 1),
      expand = expansion(mult = c(0, 0.01))
    ) +
    coord_cartesian(ylim = c(-0.09, 1.04), clip = "off") +
    guides(
      color = "none",
      fill = guide_legend(title = NULL, override.aes = list(color = c("#474747", "#474747"), linewidth = 0.25))
    ) +
    labs(x = NULL, y = "Contribution") +
    theme_bw(base_family = font_family, base_size = 10.5) +
    theme(
      panel.grid = element_blank(),
      panel.border = element_rect(color = "#606060", fill = NA, linewidth = 0.52),
      axis.title.y = element_text(size = 10.5, color = text_color, margin = margin(r = 4)),
      axis.text.y = element_text(size = 9.5, color = text_color, margin = margin(r = 2)),
      axis.ticks.y = element_line(color = "#606060", linewidth = 0.45),
      axis.ticks.length = grid::unit(2.8, "pt"),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      legend.text = element_text(size = 10.0, color = text_color),
      legend.key.size = grid::unit(10, "pt"),
      legend.spacing.x = grid::unit(5, "pt"),
      plot.margin = margin(3, 3, 4, 3, unit = "pt")
    )

  main_plot + inset_element(
    build_inset(region),
    left = 0.54, bottom = 0.55, right = 0.97, top = 0.91,
    align_to = "panel", on_top = TRUE, clip = TRUE
  )
}

panels <- lapply(region_order, build_panel)
figure <- wrap_plots(panels, ncol = 2, byrow = TRUE, guides = "collect") +
  plot_layout(heights = rep(1, 4)) &
  theme(
    text = element_text(family = font_family),
    legend.position = "top",
    legend.justification = "center",
    legend.margin = margin(0, 0, 2, 0, unit = "pt")
  )

png_file <- file.path(output_dir, "Figure4_unified_style.png")
pdf_file <- file.path(output_dir, "Figure4_unified_style.pdf")
tiff_file <- file.path(output_dir, "Figure4_unified_style.tiff")

ggsave(png_file, figure, device = ragg::agg_png, width = 7.2, height = 8.4, units = "in", dpi = 600, background = "white")
ggsave(pdf_file, figure, device = grDevices::cairo_pdf, width = 7.2, height = 8.4, units = "in", bg = "white", family = font_family)
ggsave(tiff_file, figure, device = ragg::agg_tiff, width = 7.2, height = 8.4, units = "in", dpi = 600, background = "white", compression = "lzw")

cat(normalizePath(png_file, winslash = "/", mustWork = TRUE), "\n")
cat(normalizePath(pdf_file, winslash = "/", mustWork = TRUE), "\n")
cat(normalizePath(tiff_file, winslash = "/", mustWork = TRUE), "\n")
