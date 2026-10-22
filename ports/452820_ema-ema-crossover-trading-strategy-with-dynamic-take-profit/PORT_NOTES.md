# #452820 EMA-交叉动态止盈止损交易策略-EMA-Crossover-Trading-Strategy-with-Dynamic-Take-Profit-and-Stop-Loss -> `fmz_452820_ema12_26_cross_fill_bracket_reversal`

- FMZ source id: 452820 (lineage).
- Source: https://www.fmz.com/strategy/452820 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-29 16:55:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.025, 0.05] x `tp_pct` [0.08, 0.04]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Bracket from the fill bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
