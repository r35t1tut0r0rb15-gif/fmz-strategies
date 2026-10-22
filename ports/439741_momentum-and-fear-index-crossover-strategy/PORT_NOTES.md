# #439741 Momentum and Fear Index Crossover Strategy -> `fmz_439741_momentum_crash_warning_short`

- FMZ source id: 439741 (lineage).
- Source: https://www.fmz.com/strategy/439741 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 14:27:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C124). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit momentum tests -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [50, 20] x `scale` [42000.0, 4200.0]: **4 trials**; VIX fix 22 fixed.

## Ambiguities resolved

- Price-unit comparisons as fractions of the close. Short only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
