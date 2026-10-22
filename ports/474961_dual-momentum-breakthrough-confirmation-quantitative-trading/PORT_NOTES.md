# #474961 Dual Momentum Breakthrough Confirmation Quantitative Trading Strategy -> `fmz_474961_wpr30_rsi7_joint_extreme_cross_reversal`

- FMZ source id: 474961 (lineage).
- Source: https://www.fmz.com/strategy/474961 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:37:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Joint %R / RSI extreme crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wpr_length` [30, 14] x `rsi_length` [7, 14]: **4 trials**; the levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
