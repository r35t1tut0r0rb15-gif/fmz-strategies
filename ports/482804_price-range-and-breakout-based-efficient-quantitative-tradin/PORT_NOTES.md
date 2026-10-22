# #482804 Price Range and Breakout Based Efficient Quantitative Trading Strategy -> `fmz_482804_zigzag10_consolidation5_zone_break_reversal`

- FMZ source id: 482804 (lineage).
- Source: https://www.fmz.com/strategy/482804 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:46:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Zigzag pivot breaks of a consolidation zone |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`prd` [10, 20] x `conslen` [5, 10]: **4 trials**.

## Ambiguities resolved

- highestbars(prd) == 0 ties count as the current bar. change(pp) with an na side is false.
- The 1000-bar loop cap is not applied (beyond the data at 5-day bars). MPL 2.0 source, ported and stated.
- REVERSAL INTENDED. FREQ = "5D" (five broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
