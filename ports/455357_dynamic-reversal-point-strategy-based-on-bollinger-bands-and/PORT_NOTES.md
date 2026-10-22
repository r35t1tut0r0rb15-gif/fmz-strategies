# #455357 Dynamic Reversal Point Strategy Based on Bollinger Bands and Fractal Breakouts -> `fmz_455357_fractal_entries_reversal`

- FMZ source id: 455357 (lineage).
- Source: https://www.fmz.com/strategy/455357 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-28 15:06:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fractal entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [5, 7]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
