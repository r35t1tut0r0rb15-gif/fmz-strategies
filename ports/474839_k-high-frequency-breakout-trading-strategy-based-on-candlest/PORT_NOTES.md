# #474839 基于K线收盘方向的高频交易突破策略-High-Frequency-Breakout-Trading-Strategy-Based-on-Candlestick-Close-Direction -> `fmz_474839_candle_colour_reversal_doji_counter_close`

- FMZ source id: 474839 (lineage).
- Source: https://www.fmz.com/strategy/474839 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 14:35:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C224). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle-colour reversals with a counter close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (no inputs; the counter close as written).

## Ambiguities resolved

- The counter close fires only after a doji bar, as written. REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
