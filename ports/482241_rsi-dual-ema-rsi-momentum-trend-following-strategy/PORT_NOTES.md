# #482241 双均线-RSI动量趋势跟踪策略-Dual-EMA-RSI-Momentum-Trend-Following-Strategy -> `fmz_482241_ema6_82_cross_close_dir_rsi_always_in`

- FMZ source id: 482241 (lineage).
- Source: https://www.fmz.com/strategy/482241 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-17 10:51:53). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs, RSI levels and the previous close. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [6, 12] x `slow` [82, 50]: **4 trials**; defaults 6 / 82 (the source's); RSI 14 (70 / 22) fixed.

## Ambiguities resolved

- `ta.highest(close[1], 1)` is the previous close. REVERSAL INTENDED (always in). Daily bars: broker days stamped
  with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
