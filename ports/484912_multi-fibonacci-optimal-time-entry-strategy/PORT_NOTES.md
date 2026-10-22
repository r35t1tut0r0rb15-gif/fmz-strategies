# #484912 Multi Fibonacci Optimal Time Entry Strategy -> `fmz_484912_swing20_fib705_618_cross_reversal`

- FMZ source id: 484912 (lineage).
- Source: https://www.fmz.com/strategy/484912 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-05 09:45:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C262). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Swing Fibonacci retracement crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 1 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50, 10]: **3 trials**; levels 0.705 / 0.618.

## Ambiguities resolved

- REVERSAL INTENDED, no other exit. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
