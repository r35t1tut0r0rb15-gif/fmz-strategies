# #473262 Enhanced Multi Indicator Trend Reversal Intelligence Strategy -> `fmz_473262_macd6_13_5_cross_ema20_50_rsi_filter_reversal`

- FMZ source id: 473262 (lineage).
- Source: https://www.fmz.com/strategy/473262 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:04:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings with trend and RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and levels are constants).

## Ambiguities resolved

- The take-profit is never sent (as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
