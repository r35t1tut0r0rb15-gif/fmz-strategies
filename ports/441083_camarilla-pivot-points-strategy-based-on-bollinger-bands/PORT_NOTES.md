# #441083 Camarilla Pivot Points Strategy Based on Bollinger Bands -> `fmz_441083_camarilla_l1_prev_day_reversal`

- FMZ source id: 441083 (lineage).
- Source: https://www.fmz.com/strategy/441083 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 14:23:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed days |
| 2 | PASS | Camarilla levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level_k` [0.0916, 0.183]: **2 trials** (the L1 / L2 coefficients).

## Ambiguities resolved

- Previous broker day's levels; S1 -> H1 and R1 -> L1 as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
