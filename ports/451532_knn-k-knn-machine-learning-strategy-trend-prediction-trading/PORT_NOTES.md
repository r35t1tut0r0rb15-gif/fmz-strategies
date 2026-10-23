# #451532 KNN-机器学习策略基于-K-近邻算法的趋势预测交易系统-KNN-Machine-Learning-Strategy-Trend-Prediction-Trading-System-Based-on-K-Nearest-Neighbors-Algorithm -> `fmz_451532_knn_closest_values_average_turns_reversal`

- FMZ source id: 451532 (lineage).
- Source: https://www.fmz.com/strategy/451532 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 17:09:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Turns of a nearest-neighbour smoothed average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_closest` [3, 5] x `ma_len` [5, 10]: **4 trials**; window 30, target RMA 5.

## Ambiguities resolved

- KNN slot rule as written; the short close never acts. Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "machine_learning_vote"`.

## Marks

`none`
