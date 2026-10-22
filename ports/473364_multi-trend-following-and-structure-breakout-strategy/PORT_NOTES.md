# #473364 Multi Trend Following and Structure Breakout Strategy -> `fmz_473364_ema200_trend_pullback_break5_point_bracket`

- FMZ source id: 473364 (lineage).
- Source: https://www.fmz.com/strategy/473364 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:27:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the point bracket as fractions of the signal close |
| 2 | PASS | Trend pullback breakouts with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The point bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [0.000238, 0.00238] x `tp_frac` [0.000357, 0.00357]: **4 trials**; the indicator lengths fixed.

## Ambiguities resolved

- Points as fractions of 42000 (pointvalue 1). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop`
