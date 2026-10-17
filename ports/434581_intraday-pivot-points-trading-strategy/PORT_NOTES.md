# #434581 Intraday Pivot Points Trading Strategy -> `fmz_434581_prev_day_pivot_cross_long`

- FMZ source id: 434581 (lineage).
- Source: https://www.fmz.com/strategy/434581 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-07 16:43:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | ADAPT | The tick-sized loss -> a fraction of the fill; pivot from the prior broker day |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level` ["PP", "R1"] x `sl_pct` [0.05, 0.02]: **4 trials**.

## Ambiguities resolved

- Clock rules inert on daily bars (intraday version owed); tick loss -> 5 % of the fill. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`coarse_bar_stop`
