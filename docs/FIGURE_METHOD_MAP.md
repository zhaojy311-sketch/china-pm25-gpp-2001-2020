# Manuscript figure-to-code map

This map is based on the latest supplied manuscript and the files found in the existing project. “Renderable” means that the final artwork can be regenerated from already-derived local inputs; it does not mean that the underlying scientific calculation can be reproduced.

| Figure | Manuscript content | Available script(s) | Available input | Upstream status |
|---|---|---|---|---|
| Fig. 1 | Mean GPP, GPP trend, and correlations with eight drivers | `scripts/figures/figure1_spatial_patterns.py` | Three derived XLSX tables plus boundary files | Rendering verified; upstream aggregation, trend, correlation, and significance scripts missing |
| Fig. 2 | Regional normalized variations and two-period GPP/PM2.5 trends | `scripts/figures/figure2_regional_changes.py` | Regional annual means XLSX, Fig. 1 trend XLSX, boundaries | Rendering verified; regional aggregation missing. The plotting script computes linear period slopes and fitted year-to-year percentage changes |
| Fig. 3a | Spatial relative importance of eight drivers | `scripts/figures/figure3a_spatial_importance_layout.py` | Embedded panels in a PPTX | Layout verified; values are extracted from existing artwork, not recalculated from SHAP |
| Fig. 3b | Regional SHAP-weighted relative contribution | `scripts/figures/figure3b_regional_importance.R` | Small precomputed CSV and locator GeoJSON | Rendering verified; SHAP calculation and regional weighting missing |
| Fig. 3c | SHAP dependence plots | `figure3c_extract_panels.py`, `figure3c_style_panels.py`, `figure3c_merge_dependence.py` | Existing PPTX/SVG/PNG artwork | Extraction/style/assembly verified; raw samples and SHAP calculation missing |
| Fig. 4 | Relative contributions to long-term GPP trends in two periods | `scripts/figures/figure4_trend_attribution.R` | Precomputed relative-contribution XLSX and GPP inset XLSX | Rendering verified; contribution generation, sign logic, and uncertainty calculation missing |
| Fig. 5 | Signed absolute contributions to GPP changes | `scripts/figures/figure5_absolute_contributions.py` | Precomputed absolute-contribution XLSX | Rendering and endpoint balance verified; relative-to-absolute conversion and normalization coefficient missing |
| Fig. 6 | SEM paths and direct/indirect effects | `scripts/figures/figure6_sem_diagram.py` | Source PNG and transcribed coefficients in code | Vector redraw verified; SEM fitting and diagnostics missing |

## Main claim traceability

| Manuscript claim | Existing evidence in project | Reproducibility status |
|---|---|---|
| LAI is the dominant driver | Figure 3 artwork and regional summary CSV | Can rerender; cannot recompute from fitted model |
| PM2.5 contributes roughly 10–40% regionally | Figure 4 precomputed workbook | Can inspect/rerender; upstream attribution missing |
| 2001–2013 PM2.5 contribution is −60.9 g C m−2 yr−1 and offsets 25.8% of LAI | China sheet of Figure 5 workbook: PM2.5 −60.9, LAI +236.5; `60.9 / 236.5 = 25.75%` | Arithmetic verified; generating normalization calculation missing |
| 2013–2020 PM2.5 contribution is +9.7 and equals about 20% of LAI | China sheet: PM2.5 +9.7, LAI +48.6; `9.7 / 48.6 = 19.96%` | Arithmetic verified; generating normalization calculation missing |
| SEM direct −0.0665, indirect +0.046, net approximately −0.021 | Values are transcribed in the Figure 6 script/readme | Can redraw; cannot refit or independently validate |

## Excluded legacy scripts

The original project also contains many one-variable plotting scripts with hard-coded `E:` or personal project paths. They were not promoted to the main public workflow because the consolidated Figure 1 and Figure 2 scripts supersede them and their original inputs are incomplete. They remain untouched in the source project and are listed in the quality report as legacy/unverified material.
