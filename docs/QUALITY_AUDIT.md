# Repository quality audit

## Inventory summary

- The original `王` project contains 34 source-like files outside caches and generated-output folders: 31 Python scripts, 2 R scripts, and 1 PowerShell helper. Most are visualization variants rather than analysis pipelines.
- Two additional relevant redraw scripts were found in the separate redraw workspace and promoted here: the Figure 4 R renderer and Figure 6 vector-redraw script.
- Consolidated publication figure scripts found for Figures 1, 2, 5, and 6.
- Figure 3 consists of one R renderer plus PPTX/SVG/PNG extraction and assembly scripts.
- Figure 4 consists of an R renderer reading precomputed values.
- No original end-to-end pipeline was found for preprocessing, XGBoost, SHAP calculation, trend attribution, or SEM fitting.
- Five main figure-source XLSX files were found under `绘图输入数据`; additional regional and dynamic workbooks were found at the project root.
- Large raw/project data occupy roughly 1.49 GB under the original `数据` directory and were not copied into the public candidate.
- Local dependency/cache material under `.codex-build` was excluded.

## Path and secret audit

- Personal/project absolute paths were removed from the copied main scripts and replaced with repository-relative paths.
- Legacy source scripts in the original project still contain `C:`, `D:`, and `E:` paths; the originals were not modified.
- Standard Windows font paths remain in several Figure 3 scripts as optional font candidates; they do not expose personal information.
- No API keys, access tokens, passwords, private keys, or obvious credentials were detected by the local regex scan.
- `.env`, key files, credentials, caches, generated outputs, raw scientific formats, and the review-hold data directory are excluded in `.gitignore`.

## Third-party and authorship risks

- Administrative boundary SHP/GeoJSON files have no license or source citation in the project: **do not upload**.
- Raw GOSIF-GPP, ChinaHighPM2.5, GLASS, PANDA-China, ERA5-Land, and precipitation files are third-party data: provide access instructions and citations rather than uploading them by default.
- The precipitation provider record currently states CC BY-NC-SA 4.0; confirm that any redistribution plan is compatible with the intended use.
- Figure-source PPTX/SVG/PNG assets may include work created by collaborators and are not automatically safe to redistribute.
- Because this is another author's accepted manuscript, code authorship, creator order, and contributor roles require explicit confirmation from all relevant collaborators.
- No software license should be added until rights holders approve it.

## Scientific reproducibility risks

1. Raw-data acquisition and preprocessing are undocumented in executable form.
2. The manuscript describes five-fold cross-validation and parameter optimization, while thesis material appears to mention an 80/20 split. This discrepancy must be resolved.
3. XGBoost hyperparameters, random seeds, search space, fold definitions, and trained models are missing.
4. SHAP aggregation and regional weighting are missing.
5. Figure 4 signs are manually transcribed in plotting code.
6. Figure 5 normalization coefficients and generating code are missing.
7. SEM model syntax, input data, estimator, standardized-effect method, and fit diagnostics are missing.
8. Several figure values are stored as hard-coded cells with no Excel formulas, weakening provenance.

## Current public-candidate boundary

Safe to prepare for upload after authorship/license approval:

- Cleaned source code under `scripts/`.
- README, environment files, audits, and release documentation.
- Empty output directory marker.

Not safe to upload without additional approval:

- Everything under `data/review_required/`.
- Boundary files.
- Large PPTX/SVG/PNG source artwork.
- Original raw HDF/ZIP/NetCDF/TIFF products.
- Generated figures if their publication/copyright status is unclear.

## Verdict

The package is suitable as a transparent **code-recovery and figure-rendering repository draft**, but it is not yet an end-to-end reproducibility repository. Public release should wait for the missing analytical scripts or, at minimum, a manuscript-visible limitation statement and editor-approved exception for unavailable code/data.
