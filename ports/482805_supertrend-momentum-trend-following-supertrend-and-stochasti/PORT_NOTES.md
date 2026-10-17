# #482805 动量趋势型SuperTrend与随机指标交叉策略-Momentum-Trend-Following-SuperTrend-and-Stochastic-Crossover-Strategy -> `fmz_482805_supertrend_dir_stoch_20_80_cross_2d`

- FMZ source id: 482805 (lineage).
- Source: https://www.fmz.com/strategy/482805 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:55:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A SuperTrend and a stochastic. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `k_len` [14, 21]: **4 trials**; defaults 3 / 14 (the source's); ATR 10, smoothing 3 and the
80 / 20 levels fixed.

## Ambiguities resolved

- `direction == 1` is a SuperTrend DOWN-trend in Pine: the longs are taken in down-trends and closed when it turns
  up (shorts mirrored). Ported as written.
- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850).
- REVERSAL INTENDED. Two-day bars: blocks of broker-day dates from 1970-01-01 (decision owed, #426509).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
