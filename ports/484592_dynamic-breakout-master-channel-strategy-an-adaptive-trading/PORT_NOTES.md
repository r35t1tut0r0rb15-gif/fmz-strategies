# #484592 Dynamic Breakout Master Channel Strategy An Adaptive Trading System Based on Support and Resistance Breakouts -> `fmz_484592_pivot10_sr_zone_engine_break_reversal`

- FMZ source id: 484592 (lineage).
- Source: https://www.fmz.com/strategy/484592 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-03 10:33:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C262). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pivot support / resistance zone breaks |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [10, 5] x `channel_width` [5, 3]: **4 trials**; lookback 290, range 300, min strength 1, 6 zones tested.

## Ambiguities resolved

- The zone ordering step's half swap is kept as written. MPL 2.0 source, ported and stated.
- REVERSAL INTENDED, no other exit. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
