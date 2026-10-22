# #481394 双均线与随机RSI趋势跟踪策略-Dual-EMA-and-Stochastic-RSI-Trend-Following-Strategy -> `fmz_481394_ema9_21_cross_stochrsi_extreme_reversal`

- FMZ source id: 481394 (lineage).
- Source: https://www.fmz.com/strategy/481394 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 16:56:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C243). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with Stochastic RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; Stoch RSI 14 / 14 / 3, 20 / 80.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
