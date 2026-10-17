# #483106 趋势增强型RSI-ADX线性回归预测交易策略-Enhanced-Trend-RSI-ADX-Linear-Regression-Prediction-Trading-Strategy -> `fmz_483106_rsi_exit_extreme_adx_linreg_reversal`

- FMZ source id: 483106 (lineage).
- Source: https://www.fmz.com/strategy/483106 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:46:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI, ADX and a rolling regression. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [25.0, 20.0] x `lookback` [20, 50]: **4 trials**; defaults 25 / 20 (the source's); RSI 14 (30 / 70) and DMI
14 / 14 fixed.

## Ambiguities resolved

- The "ML" prediction is the 20-bar least-squares line of close on bar_index at the current bar (`ta.linreg(close,
  20, 0)`), computed with centred x (the same line, better numerics).
- REVERSAL INTENDED (always in once started); no exits or stops. FREQ = "1h" ("5min" in the title is a label).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
