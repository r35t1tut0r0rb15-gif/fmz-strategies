# #483063 基于EMA交叉与RSI过滤的自适应动态止盈止损策略-Adaptive-Dynamic-Stop-Loss-and-Take-Profit-Strategy-Based-on-EMA-Crossover-and-RSI-Filter -> `fmz_483063_ema9_21_cross_rsi14_atr2_5_bracket_reversal`

- FMZ source id: 483063 (lineage).
- Source: https://www.fmz.com/strategy/483063 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:06:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C256). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an RSI filter and an ATR bracket |
| 3 | PASS |  |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [2.5, 1.5] x `fast_length` [9, 5]: **4 trials**; EMA 21, ATR 14, RSI 14 / 30 / 70, target 2 x stop; the bar size is the driver's (bar_size_pending).

## Ambiguities resolved

- No bar size: bar_size_pending. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`bar_size_pending`
