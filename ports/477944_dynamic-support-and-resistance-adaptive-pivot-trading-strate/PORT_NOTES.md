# #477944 Dynamic Support and Resistance Adaptive Pivot Trading Strategy -> `fmz_477944_pivot2_sr_cross_near_pct_bracket_reversal`

- FMZ source id: 477944 (lineage).
- Source: https://www.fmz.com/strategy/477944 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-10 15:08:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price bracket as fractions of the fill |
| 2 | PASS | Pivot support / resistance crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot_length` [2, 5] x `distance_pct` [0.4, 1.0]: **4 trials**; stop 10 %, target 26 %.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`coarse_bar_stop`
