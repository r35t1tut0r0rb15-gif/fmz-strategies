# #438021 Exponential Moving Average Crossover Strategy -> `fmz_438021_range_midpoint_cross_once`

- FMZ source id: 438021 (lineage).
- Source: https://www.fmz.com/strategy/438021 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 11:30:21). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry (re-sent targets marked) |
| 2 | PASS | Range midpoint and rolling extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fib_level` [0.5, 0.618] x `range_len` [100, 50]: **4 trials**; the 10-bar target window fixed.

## Ambiguities resolved

- Flags never reset (one long, one short in all); target re-sends not emitted (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`trailing_stop_pending`
