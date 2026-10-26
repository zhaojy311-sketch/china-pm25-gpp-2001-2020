# PM2.5 regulation of long-term terrestrial GPP trends across China (2001–2020)

This repository contains the figure-generation, figure-assembly, and quality-audit code prepared for the manuscript on the effects of PM2.5 changes on long-term terrestrial gross primary productivity (GPP) trends across China from 2001 to 2020.

The scripts use repository-relative paths and generate publication-ready outputs for Figures 1–6 from prepared figure-source tables and artwork.

## Included code

### Figure 1: spatial GPP patterns and driver correlations

`scripts/figures/figure1_spatial_patterns.py`

- Maps the 2001–2020 mean GPP.
- Maps the long-term GPP trend and its significance.
- Maps spatial correlations between GPP and LAI, PM2.5, precipitation, air temperature, relative humidity, VPD, PAR, and night-time light.
- Exports PDF, SVG, and high-resolution PNG files.

### Figure 2: regional temporal changes

`scripts/figures/figure2_regional_changes.py`

- Draws the national GPP trend map with eight regional locator boxes.
- Calculates period-specific linear trends for GPP and PM2.5.
- Draws regional trend bar charts and annual variation curves.
- Produces separate panels and a combined publication figure.

### Figure 3: SHAP figure rendering and assembly

`scripts/figures/figure3a_spatial_importance_layout.py`

- Extracts and arranges the spatial driver-importance panels for Figure 3a.
- Applies consistent labels, color bars, fonts, and panel spacing.

`scripts/figures/figure3b_regional_importance.R`

- Draws regional weighted-contribution bar charts for eight drivers.
- Adds regional locator maps and exports PNG, PDF, SVG, and TIFF files.

`scripts/figures/figure3c_extract_panels.py`

- Extracts the high-resolution SHAP dependence artwork embedded in PPTX and SVG source files.

`scripts/figures/figure3c_style_panels.py`

- Standardizes the fonts, axes, ticks, and frames of the SHAP dependence panels.

`scripts/figures/figure3c_merge_dependence.py`

- Renders the Figure 3c panel grid.
- Combines Figures 3a, 3b, and 3c into the complete Figure 3 layout.

### Figure 4: regional trend contributions

`scripts/figures/figure4_trend_attribution.R`

- Draws relative contributions for 2001–2013 and 2013–2020 across eight regions.
- Adds contribution directions, standard-error bars, and regional GPP trend insets.
- Exports PNG, PDF, and TIFF files.

### Figure 5: absolute GPP contributions

`scripts/figures/figure5_absolute_contributions.py`

- Draws regional waterfall charts of signed absolute contributions to GPP changes.
- Uses consistent factor colors and panel formatting.
- Checks the numerical balance between each period's starting GPP, driver contributions, and ending GPP.
- Exports PNG, PDF, and SVG files.

### Figure 6: SEM diagram rendering

`scripts/figures/figure6_sem_diagram.py`

- Produces vector artwork for the SEM pathway diagram.
- Draws the direct, indirect, and total path-effect panel.
- Exports editable SVG and PDF files.

## Audit and utility code

`scripts/audits/audit_contribution_tables.py`

- Counts formulas in the Figure 4 and Figure 5 workbooks.
- Checks whether regional relative contributions sum to one.
- Checks whether Figure 5 contributions reconcile the reported GPP endpoints.

`scripts/audits/preflight_public_tree.py`

- Scans public text files for personal absolute paths.
- Scans for common private-key, token, password, and credential patterns.

`scripts/utils/audit_panel_alignment.py`

- Provides reusable alignment and layout checks for multi-panel Matplotlib figures.

## Repository layout

```text
publication_repository/
├── README.md
├── requirements.txt
├── environment/
│   └── R-packages.txt
├── scripts/
│   ├── figures/
│   ├── audits/
│   └── utils/
├── data/
│   ├── external/
│   └── review_required/
├── docs/
└── outputs/
```

## Data products referenced by the figure scripts

| Variable | Product/source | Access route |
|---|---|---|
| GPP | GOSIF-GPP v2 | [University of New Hampshire GOSIF-GPP archive](http://data.globalecology.unh.edu/data/GOSIF-GPP_v2/) |
| PM2.5 | ChinaHighPM2.5 / CHAP | [Zenodo record 6398971](https://doi.org/10.5281/zenodo.6398971) |
| LAI | GLASS LAI | [GLASS download portal](https://www.glass.hku.hk/download.html) |
| PAR | GLASS PAR | [GLASS archive](https://glass.hku.hk/archive/PAR/) |
| Night-time light | PANDA-China | [Dataset DOI](https://doi.org/10.11888/Socioeco.tpdc.271202) |
| Temperature, relative humidity, and VPD | ERA5-Land | [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) |
| Precipitation | 1-km monthly precipitation for China | [Dataset record](https://www.tpdc.ac.cn/en/data/faae7605-a0f2-4d18-b28f-5cee413766a2/) |

Additional access and licensing notes are provided in `data/external/DATA_SOURCES.md`.

## Environment

The scripts were verified with Python 3.12.14 and R 4.5.2 on Windows.

Create the Python environment with:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

The Python dependencies include NumPy, pandas, SciPy, Matplotlib, openpyxl, and Pillow. The R package versions used for rendering are listed in `environment/R-packages.txt`.

Figures 3b and 4 use Arial. On Windows systems with non-ASCII project paths, use a UTF-8-compatible R locale or place the repository in an ASCII-only path.

## Running the figure scripts

```bash
python scripts/figures/figure1_spatial_patterns.py
python scripts/figures/figure2_regional_changes.py
python scripts/figures/figure3a_spatial_importance_layout.py
Rscript scripts/figures/figure3b_regional_importance.R
python scripts/figures/figure3c_extract_panels.py
python scripts/figures/figure3c_style_panels.py
python scripts/figures/figure3c_merge_dependence.py
Rscript scripts/figures/figure4_trend_attribution.R
python scripts/figures/figure5_absolute_contributions.py
python scripts/figures/figure6_sem_diagram.py
```

Generated files are written to figure-specific subdirectories under `outputs/`.

## Running the repository audits

```bash
python scripts/audits/audit_contribution_tables.py
python scripts/audits/preflight_public_tree.py
```

## Documentation

- `docs/SOURCE_INVENTORY.md`: mapping from the recovered source scripts to the organized repository files.
- `docs/FIGURE_METHOD_MAP.md`: mapping between manuscript figures, scripts, and input tables.
- `docs/FIG4_FIG5_FORMULA_AUDIT.md`: audit of the Figure 4 and Figure 5 contribution tables.
- `docs/REPRODUCIBILITY_REPORT.md`: local execution and output verification record.
- `docs/QUALITY_AUDIT.md`: repository quality and public-release checks.
- `docs/GITHUB_ZENODO_RELEASE_GUIDE.md`: instructions for GitHub release and Zenodo archiving.
