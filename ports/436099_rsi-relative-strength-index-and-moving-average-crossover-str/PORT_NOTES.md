# #436099 RSI指标与平均线交叉策略Relative-Strength-Index-and-Moving-Average-Crossover-Strategy -> `fmz_436099_rsi_ma_cross_extremes`

- FMZ source id: 436099 (lineage).
- Source: https://www.fmz.com/strategy/436099 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-21 11:30:27). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI cross and extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [13, 7] x `ma_len` [9, 5]: **4 trials**; levels 90 / 10 fixed.

## Ambiguities resolved

- Per-bar churn at the extremes not modelled; last entry sent stands. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
