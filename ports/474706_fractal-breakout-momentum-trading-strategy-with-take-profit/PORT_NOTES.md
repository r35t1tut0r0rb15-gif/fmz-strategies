# #474706 Fractal Breakout Momentum Trading Strategy with Take Profit Optimization -> `fmz_474706_fractal_distance_107pip_target_reversal`

- FMZ source id: 474706 (lineage).
- Source: https://www.fmz.com/strategy/474706 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 17:20:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C223). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the pip target as a fraction of the fill |
| 2 | PASS | Fractal-distance entries with a target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trig_frac` [0.002548, 0.01] x `tp_frac` [0.002548, 0.01]: **4 trials**.

## Ambiguities resolved

- Pips as fractions of 42000 of the signal close. The short wins ties. Repeat re-sends not followed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
