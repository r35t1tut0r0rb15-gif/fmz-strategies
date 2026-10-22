# #473411 Dual Chain Hybrid Momentum EMA Tracking Trading System -> `fmz_473411_dual_chain_weekly_12h_ema_entries_daily_9h_exits`

- FMZ source id: 473411 (lineage).
- Source: https://www.fmz.com/strategy/473411 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 17:04:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; completed weekly values, last lower-time-frame bars |
| 2 | PASS | Multi-time-frame EMA crossing chains |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [10, 20] x `len2` [9, 18]: **4 trials**; both chains on, the time frames as written.

## Ambiguities resolved

- Lower-time-frame bars counted from the broker day's start. A same-bar close and other-chain re-entry continue the position. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
