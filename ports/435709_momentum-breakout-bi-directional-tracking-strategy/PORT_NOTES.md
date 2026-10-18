# #435709 Momentum Breakout Bi directional Tracking Strategy -> `fmz_435709_hilo_adx_breakout`

- FMZ source id: 435709 (lineage).
- Source: https://www.fmz.com/strategy/435709 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 10:47:46). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel midpoint and a directional index |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ha` [14, 20] x `adx_threshold` [25, 20]: **4 trials**; ADX 14 and DI threshold 50 fixed.

## Ambiguities resolved

- Non-standard true range and SMA smoothing as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
