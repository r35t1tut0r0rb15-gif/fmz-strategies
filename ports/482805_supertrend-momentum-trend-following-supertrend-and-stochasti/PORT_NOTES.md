# #482805 动量趋势型SuperTrend与随机指标交叉策略-Momentum-Trend-Following-SuperTrend-and-Stochastic-Crossover-Strategy -> `fmz_482805_supertrend3_10_dir_stoch14_20_80_cross_reversal`

- FMZ source id: 482805 (lineage).
- Source: https://www.fmz.com/strategy/482805 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:55:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend direction with Stochastic level crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_length` [10, 20]: **4 trials**; Stochastic 14 / 3, levels 20 / 80.

## Ambiguities resolved

- direction == 1 is Pine's down-trend; ported as written, not as the comment says.
- REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
