# #489634 多指标结合的自适应波动ATR动态止盈止损15分钟图表趋势跟踪策略-Multi-Indicator-Adaptive-Volatility-ATR-Dynamic-SL-TP-15-Minute-Chart-Trend-Following-Strategy -> `fmz_489634_ema_macd_rsi_atr_bracket_15m`

- FMZ source id: 489634 (lineage).
- Source: https://www.fmz.com/strategy/489634 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-07 11:33:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (mark). |
| 2 | PASS | EMA, MACD, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group (the same logic as #489966 on another bar size). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.0, 2.0] x `tp_atr` [2.0, 4.0]: **4 trials**; defaults 1 / 2 (the source's); EMA 50, MACD 12 / 26 / 9,
RSI 14 (70 / 30) and ATR 14 fixed.

## Moving bracket (rule 2, mark `trailing_stop_pending`)

As #489966: the stop and target are re-computed every bar from the current close; fixed at the signal bar here.

## Ambiguities resolved

- Every condition bar is an entry; entries reverse. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
