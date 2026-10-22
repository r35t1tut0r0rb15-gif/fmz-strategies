# #440062 双均线反转与ATR-trailing-stop组合策略Combination-Strategy-of-Dual-Moving-Average-Reversal-and-ATR-Trailing-Stop -> `fmz_440062_reversal123_atr_trailing_stop_combo`

- FMZ source id: 440062 (lineage).
- Source: https://www.fmz.com/strategy/440062 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-26 11:26:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and an ATR trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `n_atr_multip` [3.5, 2.0]: **4 trials**; ATR 5 and the 123 smoothing fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
