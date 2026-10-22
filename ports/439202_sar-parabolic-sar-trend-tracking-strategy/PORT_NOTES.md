# #439202 抛物线SAR趋势追踪策略Parabolic-SAR-Trend-Tracking-Strategy -> `fmz_439202_sar_trend_trader_ema_offset`

- FMZ source id: 439202 (lineage).
- Source: https://www.fmz.com/strategy/439202 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-18 12:21:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR breaks and EMA filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [100, 50] x `offset` [1.0, 0.5]: **4 trials**; fast EMA 10 and the SAR settings fixed.

## Ambiguities resolved

- Closes before entries. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
