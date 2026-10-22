# #442113 Fractal and Pattern Based Quantitative Trading Strategy -> `fmz_442113_two_bar_breakout_fractal_pattern_reversal`

- FMZ source id: 442113 (lineage).
- Source: https://www.fmz.com/strategy/442113 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-19 14:32:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C151). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel crossings and candle patterns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`channel` [2, 3] x `fractal` [3, 5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
