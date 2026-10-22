# #440553 超级趋势RSI与EMA交叉策略SuperTrend-RSI-EMA-Crossover-Strategy -> `fmz_440553_supertrend_rsi70_ema9_long`

- FMZ source id: 440553 (lineage).
- Source: https://www.fmz.com/strategy/440553 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 16:16:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend, RSI and EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `rsi_length` [14, 7]: **4 trials**; ATR 10 and EMA 9 fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
