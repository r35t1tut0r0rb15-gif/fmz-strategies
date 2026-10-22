# #443121 Momentum Crossover Strategy with Dynamic Trailing Stop Loss -> `fmz_443121_ema9_21_cross_dmi_confirm_reversal`

- FMZ source id: 443121 (lineage).
- Source: https://www.fmz.com/strategy/443121 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-29 13:55:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a DMI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ema` [9, 5] x `di_len` [17, 14]: **4 trials**; the long EMA and the ADX smoothing fixed.

## Ambiguities resolved

- DI over the raw true range as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
