# #473360 多均线趋势追踪与RSI动量策略-Multi-MA-Trend-Following-with-RSI-Momentum-Strategy -> `fmz_473360_sma20_50_200_ordering_rsi_filter_reversal_target_pending`

- FMZ source id: 473360 (lineage).
- Source: https://www.fmz.com/strategy/473360 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:20:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA orderings with an RSI filter; per-bar target described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The point target stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and levels are constants; the target is pending).

## Ambiguities resolved

- Per-bar target pending (trailing_stop_pending); no trail. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
