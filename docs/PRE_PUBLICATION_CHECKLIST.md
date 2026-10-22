# Manual confirmation checklist

Do not make the repository public or publish a release until every blocking item is resolved.

## Blocking scientific items

- [ ] Recover the exact raw-file manifest for 2001–2020, including versions, filenames, checksums, resolutions, scale factors, and access dates.
- [ ] Recover preprocessing scripts and confirm reprojection, resampling, masks, missing-data handling, and temporal aggregation.
- [ ] Recover XGBoost training/tuning code, parameter search space, selected hyperparameters, seeds, folds, and saved metrics/models.
- [ ] Resolve the manuscript five-fold CV versus thesis 80/20 split discrepancy.
- [ ] Recover SHAP calculation and regional aggregation code plus raw or efficiently archived SHAP outputs.
- [ ] Recover the Figure 4/5 attribution script, sign rule, normalization coefficients, factor trends, and standard-error method.
- [ ] Recover SEM input data, model syntax, estimator, standardization, direct/indirect-effect calculation, and fit indices.
- [ ] Run an end-to-end reproduction and compare numeric outputs, not only figure appearance.

## Blocking ownership and licensing items

- [ ] Confirm the owner/creator of every script with the corresponding coauthors.
- [ ] Agree on the software license; replace `LICENSE_PENDING.md` with the approved license.
- [ ] Confirm the creator order and contributor roles for `CITATION.cff` and Zenodo.
- [ ] Obtain permission for any collaborator-created PPTX/SVG/PNG source artwork that will be shared.
- [ ] Identify the administrative-boundary provider and redistribution license, or replace the boundaries with a clearly licensed source.
- [ ] Review provider terms for all derived tables before redistribution.
- [ ] Confirm that no confidential review material, unpublished correspondence, tracked changes, or personal metadata will be uploaded.

## Repository checks

- [ ] Run `python scripts/audits/preflight_public_tree.py` and resolve all findings.
- [ ] Run `git status --ignored` and inspect every staged and ignored file.
- [ ] Run an independent secret scanner before first push.
- [ ] Confirm that `data/review_required/`, `outputs/`, raw raster/NetCDF/HDF files, and PPTX files are not staged.
- [ ] Validate every external data URL and citation.
- [ ] Confirm that README commands work in a fresh clone and clean environment.
- [ ] Add tests or a machine-readable workflow once missing analysis scripts are recovered.
- [ ] Add a `CITATION.cff` with approved authors, release date, repository URL, version, DOI, and license.
- [ ] Add an approved `LICENSE` file.

## Manuscript alignment

- [ ] Replace the placeholder GitHub URL in the manuscript's Open Research section.
- [ ] Add the archived software version DOI to the Availability Statement and References.
- [ ] Cite every third-party dataset and describe access conditions/licenses.
- [ ] Ensure figure captions and Methods use the same period definitions, variables, units, region abbreviations, and model validation description as the released code.
- [ ] Tell the editor explicitly if central scripts remain unavailable; do not imply full reproducibility.

## Final approval

- [ ] Corresponding author approval.
- [ ] Code creators' approval.
- [ ] Data/figure-table creators' approval.
- [ ] Institutional or funder review, if required.
- [ ] Final GitHub visibility approval.
- [ ] Final Zenodo publication approval.
