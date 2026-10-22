# #483102 Adaptive Trading Strategy Combining Dynamic Trend Reversal and Stochastic Indicator -> `fmz_483102_zigzag0_25pct_reverse_line_stoch9_tick_bracket_reversal`

- FMZ source id: 483102 (lineage).
- Source: https://www.fmz.com/strategy/483102 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:00:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; tick bracket as fractions of the fill |
| 2 | ADAPT | Tick bracket read as fractions at BTC 42000 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`percent` [0.25, 1.0] x `k_length` [9, 14]: **4 trials**; K smoothing 3, stop 2.381e-04, target 7.143e-04 of the close.

## Ambiguities resolved

- The tick bracket is read at BTC 42000 (tick 0.1). Repeat state signals re-send the bracket; pending.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
