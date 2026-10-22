# #473396 双EMA指标智能交叉交易系统与动态止盈止损策略-Dual-EMA-Indicator-Smart-Crossing-Trading-System-with-Dynamic-Stop-Loss-and-Take-Profit-Strategy -> `fmz_473396_ema9_21_cross_avg_bracket_5_10_reversal`

- FMZ source id: 473396 (lineage).
- Source: https://www.fmz.com/strategy/473396 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:33:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C218). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the average-price bracket as fixed fractions |
| 2 | PASS | EMA crossings with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND473396. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.05, 0.03] x `tp_pct` [0.10, 0.06]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
