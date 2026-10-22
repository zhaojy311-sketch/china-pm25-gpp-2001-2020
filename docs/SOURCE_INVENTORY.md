# Recovered source inventory

The original project was not modified. The table below records which original file was copied into the publication draft and how it is used.

| Public-draft file | Original file | Role | Modification in copy |
|---|---|---|---|
| `scripts/figures/figure1_spatial_patterns.py` | `王/代码/图1-GPP空间分布与相关性-10子图统一字号.py` | Figure 1 rendering | Replaced private skill import and project paths with local utility/repository paths |
| `scripts/figures/figure2_regional_changes.py` | `王/代码/图2-八大区域变化组合图.py` | Figure 2 rendering and simple period regressions | Replaced hard-coded project paths only |
| `scripts/figures/figure3a_spatial_importance_layout.py` | `王/代码/8驱动因子贡献率空间分布-精简标签.py` | Extract/relabel Figure 3a embedded panels | Replaced project paths only |
| `scripts/figures/figure3b_regional_importance.R` | `王/Fig3b--SHAP_regional_facets_locator_package/923放大内嵌子图/plot_SHAP_regional_facets.R` | Figure 3b regional bar facets | Added repository-relative defaults; plotting logic unchanged |
| `scripts/figures/figure3c_extract_panels.py` | `王/代码/提取PPT中高分辨率SHAP图.py` | Extract Figure 3c artwork | Replaced project paths only |
| `scripts/figures/figure3c_style_panels.py` | `王/代码/统一Figure3c投稿样式.py` | Style Figure 3c SVG | Replaced project paths only |
| `scripts/figures/figure3c_merge_dependence.py` | `王/代码/SHAP依赖图统一字号并合并三图.py` | Render/merge Figure 3c and full Figure 3 | Replaced project paths only |
| `scripts/figures/figure4_trend_attribution.R` | `文章重新绘图/Figure4_统一风格绘图.R` | Figure 4 rendering | Points to the recovered dynamic contribution workbook and repository output directory |
| `scripts/figures/figure5_absolute_contributions.py` | `王/代码/Figure5_实际贡献瀑布图_统一样式.py` | Figure 5 rendering and endpoint reconciliation | Replaced project path and private utility import |
| `scripts/figures/figure6_sem_diagram.py` | `文章重新绘图/redraw_fig6.py` | Figure 6 vector redraw | Replaced source/output paths only |
| `scripts/utils/audit_panel_alignment.py` | `王/代码/audit_panel_alignment.py` | Figure panel-alignment QA | Copied unchanged |

## Legacy scripts retained only in the original project

The original `王/代码` directory also contains per-variable maps, regional line/bar prototypes, a significance map, an R2 plot, and an EMF helper. They were not copied because the consolidated scripts above cover the manuscript figures, many legacy scripts contain obsolete absolute paths, and several required inputs are absent. No legacy file was deleted or edited.

## Dependency flow of recovered assets

```text
raw external products
    └── [missing preprocessing and aggregation]
          ├── Figure 1/2 derived tables ──> Figure 1 and Figure 2 renderers
          ├── [missing XGBoost training]
          │     └── [missing SHAP calculation/aggregation]
          │           └── existing Figure 3 CSV/artwork ──> Figure 3 renderers
          ├── [missing trend attribution/sign/normalization]
          │     ├── existing relative table ──> Figure 4 renderer
          │     └── existing absolute table ──> Figure 5 renderer
          └── [missing SEM fit]
                └── existing coefficients/artwork ──> Figure 6 redraw
```

This dependency graph is the central limitation of the current package: the terminal plotting nodes exist, while most analysis-producing nodes do not.
