# #474681 动态RSI震荡多项式拟合指标趋势量化交易策略-Dynamic-RSI-Oscillator-Polynomial-Fitting-Indicator-Trend-Quantitative-Trading-Strategy -> `fmz_474681_delta_rsi_poly2_slope_zero_cross_reversal`

- FMZ source id: 474681 (lineage).
- Source: https://www.fmz.com/strategy/474681 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 15:32:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Polynomial-fit RSI slope crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [21, 14] x `window` [21, 30]: **4 trials**; order 2, Zero-Crossing conditions.

## Ambiguities resolved

- Conditions Zero-Crossing (defaults); RMSE filter off. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
