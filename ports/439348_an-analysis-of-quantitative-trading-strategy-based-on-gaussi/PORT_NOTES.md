# #439348 An Analysis of Quantitative Trading Strategy Based on Gaussian Error Function -> `fmz_439348_p_signal_erf_turn_long`

- FMZ source id: 439348 (lineage).
- Source: https://www.fmz.com/strategy/439348 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 14:28:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A smoothed statistic of price changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n_points` [9, 15, 25]: **3 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
