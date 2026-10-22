# #483111 Dynamic Opening Range Breakout High Frequency Trading Strategy -> `fmz_483111_ny_0930_0945_orb_half_range_stop_1_5_range_target`

- FMZ source id: 483111 (lineage).
- Source: https://www.fmz.com/strategy/483111 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 14:02:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; range stop and target as fractions of the fill |
| 2 | PASS | New York opening-range breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_frac` [0.5, 0.25] x `target_mult` [3.0, 2.0]: **4 trials**; range 09:30-09:45 New York, days Tue / Wed / Fri.

## Ambiguities resolved

- The weekday is read in UTC (dayofweek of the header exchange); the range in New York time. The target is ported from the fill.
- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "opening_range"`.

## Marks

`none`
