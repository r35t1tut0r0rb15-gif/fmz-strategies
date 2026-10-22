# #458027 MACD交叉动量策略与动态止盈止损优化-MACD-Crossover-Momentum-Strategy-with-Dynamic-Take-Profit-and-Stop-Loss-Optimization -> `fmz_458027_macd_cross_point_bracket_reversal`

- FMZ source id: 458027 (lineage).
- Source: https://www.fmz.com/strategy/458027 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 13:35:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C198). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the price-unit bracket as fractions of 42000 |
| 2 | PASS | MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [0.00119, 0.01] x `tp_frac` [0.00238, 0.02]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- Points as fractions of 42000. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
