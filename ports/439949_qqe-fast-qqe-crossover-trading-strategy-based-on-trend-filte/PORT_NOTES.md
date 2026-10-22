# #439949 基于趋势过滤的快速QQE交叉策略Fast-QQE-Crossover-Trading-Strategy-Based-on-Trend-Filter -> `fmz_439949_qqe_threshold_direction_filter`

- FMZ source id: 439949 (lineage).
- Source: https://www.fmz.com/strategy/439949 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-25 11:34:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C127). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed RSI runs and MA direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The point inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`threshold` [10, 5] x `len2` [20, 50]: **4 trials**; RSI 6 / 3 and SMA 50 fixed.

## Ambiguities resolved

- Offset-free trailing exit places nothing. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
