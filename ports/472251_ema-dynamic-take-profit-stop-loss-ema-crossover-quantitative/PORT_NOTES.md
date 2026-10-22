# #472251 EMA双均线交叉动态止盈止损量化交易策略-Dynamic-Take-Profit-Stop-Loss-EMA-Crossover-Quantitative-Trading-Strategy -> `fmz_472251_ema10_26_cross_pip_bracket_one_trade_flag`

- FMZ source id: 472251 (lineage).
- Source: https://www.fmz.com/strategy/472251 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-18 15:53:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the pip bracket as fractions of the fill |
| 2 | PASS | EMA crossings with a pip bracket, one trade at a time |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_frac` [0.000714, 0.02] x `sl_frac` [0.000238, 0.01]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Pips as fractions of 42000; the flag cleared by close tests only (as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
