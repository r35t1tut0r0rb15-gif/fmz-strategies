# #472248 多重EMA交叉趋势跟踪与动态止盈止损优化策略-Multi-EMA-Crossover-Trend-Following-Strategy-with-Dynamic-Stop-Loss-and-Take-Profit-Optimization -> `fmz_472248_ema21_50_cross_ema200_side_tick_bracket_reversal`

- FMZ source id: 472248 (lineage).
- Source: https://www.fmz.com/strategy/472248 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-18 15:44:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C211). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples |
| 2 | PASS | EMA crossings with a trend filter and a tick bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.005, 1.0] x `tp_atr` [0.01, 2.0]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Ticks as ATR multiples (1D ~1000). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
