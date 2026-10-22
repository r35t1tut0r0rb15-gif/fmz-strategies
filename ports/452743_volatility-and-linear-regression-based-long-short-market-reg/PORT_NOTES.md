# #452743 Volatility and Linear Regression based Long Short Market Regime Optimization Strategy -> `fmz_452743_linreg_offset_difference_atr_band_reversal`

- FMZ source id: 452743 (lineage).
- Source: https://www.fmz.com/strategy/452743 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 17:40:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the price-unit thresholds as fractions of 42000 |
| 2 | PASS | Regression-difference regimes beyond an ATR band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 20] x `atr_mult` [2.0, 1.0] x `thr_frac` [2.38e-05, 0.001]: **8 trials**; the ATR length fixed.

## Ambiguities resolved

- The 'slope' sign as written; thresholds as fractions of 42000. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
