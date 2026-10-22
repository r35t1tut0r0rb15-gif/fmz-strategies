# #489309 Dow Theory Trend Adaptive Momentum Strategy -> `fmz_489309_dow_pivot10_hh_hl_trend_change_tick_bracket_reversal`

- FMZ source id: 489309 (lineage).
- Source: https://www.fmz.com/strategy/489309 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 13:05:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; tick bracket from the fill |
| 2 | ADAPT | Tick bracket read as percents at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivotLookback` [10, 5] x `sl_pct` [0.1667, 0.5]: **4 trials** (target 2 x the stop).

## Ambiguities resolved

- Ticks read at BNB 600. REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "market_structure"`.

## Marks

`none`
