# #489187 Ghost Moving Average with Momentum Integration and Fibonacci Target Stop Loss Strategy -> `fmz_489187_ghost_ma20_cross_momentum_fib_range_bracket_reversal`

- FMZ source id: 489187 (lineage).
- Source: https://www.fmz.com/strategy/489187 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 15:33:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C270). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; range bracket as fractions of the fill |
| 2 | PASS | Hull-type MA crossings with momentum and a Fibonacci-range bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gmaLength` [20, 50] x `swingLookback` [50, 20]: **4 trials**; momentum 20 / 10.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "3D" (three broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
