# #458051 高级EMA交叉策略基于动态止损和获利目标的自适应交易系统Advanced-EMA-Crossover-Strategy-Adaptive-Trading-System-with-Dynamic-Stop-Loss-and-Take-Profit-Targets -> `fmz_458051_ema9_26_cross_tick_bracket_reversal`

- FMZ source id: 458051 (lineage).
- Source: https://www.fmz.com/strategy/458051 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 15:20:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.06, 1.0] x `tp_atr` [0.18, 3.0]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Ticks as ATR multiples (1h ~150). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
