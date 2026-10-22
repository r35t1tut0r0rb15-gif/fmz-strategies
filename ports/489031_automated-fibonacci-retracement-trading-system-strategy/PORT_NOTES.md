# #489031 Automated Fibonacci Retracement Trading System Strategy -> `fmz_489031_fib20_618_382_cross_pct_bracket_reversal`

- FMZ source id: 489031 (lineage).
- Source: https://www.fmz.com/strategy/489031 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 13:25:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | Fibonacci level crossings with a percent bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 50] x `tp_pct` [2.0, 4.0]: **4 trials** (stop half the target).

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "fibonacci"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
