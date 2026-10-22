# SHAP calculation code missing

The project contains Figure 3 layout/assembly scripts and a small regional weighted-contribution CSV, but no code that loads a fitted XGBoost model, calls SHAP, saves raw SHAP arrays, computes mean absolute SHAP importance, or aggregates pixel values into regions.

The thesis describes global importance conceptually as the mean absolute SHAP value, but that description is not a substitute for the original executable pipeline.
