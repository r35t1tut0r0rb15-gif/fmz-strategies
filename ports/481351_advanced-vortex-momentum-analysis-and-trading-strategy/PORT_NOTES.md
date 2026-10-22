# #481351 Advanced Vortex Momentum Analysis and Trading Strategy -> `fmz_481351_vortex14_cross_reversal`

- FMZ source id: 481351 (lineage).
- Source: https://www.fmz.com/strategy/481351 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 14:38:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Vortex crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21, 7]: **3 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "vortex"`.

## Marks

`none`
