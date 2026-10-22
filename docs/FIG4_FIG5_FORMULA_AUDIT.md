# Figure 4–5 contribution calculation audit

## Verified observations

1. `Figure4_relative_contributions.xlsx` contains precomputed relative contribution magnitudes and standard errors. It contains **zero Excel formulas**.
2. For every region and period, the nonzero relative contributions sum to 1.0 within floating-point precision. The workbook therefore stores normalized shares.
3. `figure4_trend_attribution.R` only reads those values (`lines 65–73` and `119–126`) and plots them. It does not calculate SHAP values or normalize contributions.
4. The positive/negative arrows in Figure 4 are manually encoded in the `directions` list (`lines 45–58`) and described in the source comment as transcribed from the supplied sample figure. They are not derived from the workbook.
5. `Figure5_absolute_contributions.xlsx` contains signed, precomputed absolute contributions and period endpoints. It contains **zero Excel formulas**.
6. `figure5_absolute_contributions.py` loads the values (`line 102`), draws the waterfall, and checks `start + sum(contributions) - end` (`lines 131–143`). It does not convert Figure 4 shares into Figure 5 values.

## SHAP importance formula supported by the thesis text

For feature `i` and observations `j = 1, ..., n`, the thesis describes global feature importance as mean absolute SHAP magnitude:

```text
I_i = (1 / n) * sum_j |phi_ij|
```

The standard normalized share consistent with the Figure 4 workbook is:

```text
RC_i = I_i / sum_k I_k
```

The second equation is consistent with the workbook sums but was **not found as executable code** in the supplied project. It must be confirmed against the original analysis.

SHAP additivity is conceptually:

```text
f(x_j) = E[f(X)] + sum_i phi_ij
```

The sign of `phi_ij` indicates the direction of a feature's contribution for observation `j`. However, the exact rule used to turn observation-level SHAP signs into the period-level arrows in Figure 4 was not found.

## Figure 5 absolute contributions

The only formula directly verified in code is the endpoint identity:

```text
GPP_end ≈ GPP_start + sum_i A_i
```

where `A_i` is the signed absolute contribution already stored in the Figure 5 workbook. The local audit found residuals of 0 for most region-periods and ±1 g C m−2 yr−1 for a few, consistent with integer endpoint rounding.

The manuscript narrative implies a conversion of normalized, signed shares to absolute contributions using a period-specific scaling/normalization coefficient. Algebraically, a common form would be:

```text
A_i = K * s_i * RC_i
K = Delta_GPP / sum_i (s_i * RC_i)
```

where `s_i` is a direction sign and `Delta_GPP = GPP_end - GPP_start`. **This is shown only as the algebra that would satisfy the endpoint constraint; it is not verified as the authors' implemented formula.** No original code, `K` values, factor-trend inputs, or uncertainty propagation was found. The repository must not present this inferred form as the actual method without author confirmation.

## National ratios used in the manuscript

From the China worksheet in the supplied Figure 5 workbook:

```text
2001–2013: |−60.9| / 236.5 = 0.2575 ≈ 25.8%
2013–2020: 9.7 / 48.6 = 0.1996 ≈ 20.0%
```

These two ratios are reproducible arithmetic on the stored final contributions. They do not validate how the stored contributions were generated.

## Required recovery items

- Original SHAP arrays or a deterministic script that recalculates them.
- Exact spatial and temporal weighting used for regional aggregation.
- Rule that assigns each factor's period-level positive/negative direction.
- Definition and stored values of the normalization coefficient for every region and period.
- Factor trend inputs and units.
- Method used to calculate standard errors in Figure 4.
- Script that writes both Figure 4 and Figure 5 workbooks from model output.

Until those items are recovered, Figures 4–5 are auditable as final tables and internally checkable, but not reproducible from model output.
