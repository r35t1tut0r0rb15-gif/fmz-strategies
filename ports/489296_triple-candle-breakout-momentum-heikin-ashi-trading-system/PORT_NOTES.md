# #489296 三次蜡烛突破动量平滑平均交易策略-Triple-Candle-Breakout-Momentum-Heikin-Ashi-Trading-System -> `fmz_489296_heikin_ashi_colour_change_breakout`

- FMZ source id: 489296 (lineage).
- Source: https://www.fmz.com/strategy/489296 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:17:32). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders (breaks checked on the completed bar) |
| 2 | PASS | Candle levels only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n_opposite` [3, 2]: **2 trials**; 3 is the source's (it has no inputs).

## Ambiguities resolved

- nz() seeds each level with 0, so nothing fires before the first setup; the breakout needs the previous bar's HA
  high (low) to equal the stored level, i.e. the bar right after the setup.
- The script's active flags are tracked apart from the position; closes act on the position held at the bar's start.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`none`
