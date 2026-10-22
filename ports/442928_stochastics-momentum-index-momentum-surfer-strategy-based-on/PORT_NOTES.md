# #442928 基于-Stochastics-Momentum-Index-的趋势追踪策略Momentum-Surfer-Strategy-Based-on-Stochastics-Momentum-Index -> `fmz_442928_smi_signal_ema_cross_extreme_reversal`

- FMZ source id: 442928 (lineage).
- Source: https://www.fmz.com/strategy/442928 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 14:32:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMI crossings at the extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG442928. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`a` [10, 20] x `ob` [40, 30]: **4 trials** (oversold = -ob); the smoothing lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
