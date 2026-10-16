# #430124 Glory Hole Breakout Strategy -> `fmz_430124_glory_hole_sma_adx`

- FMZ source id: 430124 (lineage).
- Source: https://www.fmz.com/strategy/430124 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-25 11:35:36). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A moving average against the bar and an ADX level. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `adx_level` [30, 20]: **4 trials**; ADX 14 / 14 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
