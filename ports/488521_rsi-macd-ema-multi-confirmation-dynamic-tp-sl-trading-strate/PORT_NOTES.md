# #488521 多重确认动态止盈止损交易策略RSI与MACD结合EMA趋势和蜡烛形态识别-Multi-Confirmation-Dynamic-TP-SL-Trading-Strategy-RSI-and-MACD-Combined-with-EMA-Trend-and-Candlestick-Pattern-Recognition -> `fmz_488521_engulf_pinbar_rsi_macd_atr_bracket`

- FMZ source id: 488521 (lineage).
- Source: https://www.fmz.com/strategy/488521 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-28 15:37:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Candle proportions, EMA, oscillators and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `ema_len` [50, 100]: **4 trials**; defaults 1.5 / 50 (the source's fixed values); RSI 14,
MACD 12 / 26 / 9, ATR 14 and the 2.5 shadow ratio fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new signal bar (its `strategy.exit`). The port
keeps the entry's bracket (fixed at the signal bar, re-based on the fill).

## Ambiguities resolved

- Buy and sell need opposite sides of the EMA: never on one bar. REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`trailing_stop_pending`
