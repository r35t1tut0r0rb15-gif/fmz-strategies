# #435143 Trend Tracking Strategy Based on Dual Vortex Indicator Combined with True Strength Index -> `fmz_435143_tsi_vortex_cross_one_bar`

- FMZ source id: 435143 (lineage).
- Source: https://www.fmz.com/strategy/435143 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 16:23:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TSI and Vortex crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [14, 28] x `bar` [1, 3]: **4 trials**; TSI 25 / 13 / 13 fixed.

## Ambiguities resolved

- One-bar holding as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
