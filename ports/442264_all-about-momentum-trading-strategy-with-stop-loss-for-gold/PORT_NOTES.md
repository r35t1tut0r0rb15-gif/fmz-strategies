# #442264 All About Momentum Trading Strategy with Stop Loss for Gold -> `fmz_442264_ema21_zscore_cross_reversal`

- FMZ source id: 442264 (lineage).
- Source: https://www.fmz.com/strategy/442264 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 16:27:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C153). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Z-score crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [21, 50] x `entry_z` [0.5, 1.0]: **4 trials**; the stop level 3 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
