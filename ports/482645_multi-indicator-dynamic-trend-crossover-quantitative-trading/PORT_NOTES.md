# #482645 Multi Indicator Dynamic Trend Crossover Quantitative Trading Strategy -> `fmz_482645_macd_and_ema9_21_same_bar_cross_rsi_reversal`

- FMZ source id: 482645 (lineage).
- Source: https://www.fmz.com/strategy/482645 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 15:01:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Coincident MACD and EMA crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ema_length` [9, 5] x `slow_ema_length` [21, 34]: **4 trials**; MACD 12 / 26 / 9, RSI 14, 30 / 70.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
