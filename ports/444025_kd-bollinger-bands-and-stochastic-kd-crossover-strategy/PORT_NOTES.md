# #444025 布林带与随机指标KD交叉策略Bollinger-Bands-and-Stochastic-KD-Crossover-Strategy -> `fmz_444025_lower_band_stoch_cross_long`

- FMZ source id: 444025 (lineage).
- Source: https://www.fmz.com/strategy/444025 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 16:49:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic crossings at the lower band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `kd_length` [14, 9]: **4 trials**; the multiplier and smoothing fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
