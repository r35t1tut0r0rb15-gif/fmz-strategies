# #483117 ATR动态趋势跟踪与均线交叉交易策略-ATR-Dynamic-Trend-Following-and-EMA-Crossover-Trading-Strategy -> `fmz_483117_ut_bot_atr_trail_cross_1d`

- FMZ source id: 483117 (lineage).
- Source: https://www.fmz.com/strategy/483117 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 16:57:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR trailing level. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `atr_len` [10, 14]: **4 trials**; defaults 1 / 10 (the source's); Heikin Ashi source off.

## Ambiguities resolved

- The trail starts as `var ... = na`, so the first level is src + nLoss and the ratchet needs a non-na previous level
  (differs from the `nz(..., 0)` UT Bot variant of #492009 / #489301). `ema(src, 1)` is src.
- REVERSAL INTENDED (always in the market); no exits or stops. Broker days stamped with their first minute (as
  #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
