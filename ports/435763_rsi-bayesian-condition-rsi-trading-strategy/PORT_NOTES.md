# #435763 应用贝叶斯条件判断的RSI交易策略Bayesian-Condition-RSI-Trading-Strategy -> `fmz_435763_bayes_conditional_rsi_moves`

- FMZ source id: 435763 (lineage).
- Source: https://www.fmz.com/strategy/435763 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-18 17:09:00). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Move counts and an RSI jump |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p` [30, 20] x `t` [1.003, 1.01]: **4 trials**; look range 7, jump 8, smoothing 3 and RSI 14 fixed.

## Ambiguities resolved

- Counts on bars t-1..t-p; RSI of the open; missing counts as else. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bayesian_counts"`.

## Marks

`none`
