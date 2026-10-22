# #476269 基于动量指标的SMI交叉信号自适应预测策略-Momentum-Based-SMI-Crossover-Signal-Adaptive-Prediction-Strategy -> `fmz_476269_smi14_signal_cross_reversal`

- FMZ source id: 476269 (lineage).
- Source: https://www.fmz.com/strategy/476269 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-27 15:38:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMI signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_k` [14, 21] x `length_d` [3, 5]: **4 trials**; signal EMA 3.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
