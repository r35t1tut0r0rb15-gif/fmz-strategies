# #439839 基于线性回归RSI的量化交易策略Quantitative-Trading-Strategy-Based-on-Linear-Regression-RSI -> `fmz_439839_linear_regression_rsi_ema_cross_long`

- FMZ source id: 439839 (lineage).
- Source: https://www.fmz.com/strategy/439839 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 11:35:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI of a regression line and its EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [200, 100] x `ema_fast` [50, 20]: **4 trials**; RSI 21 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
