# #488521 多重确认动态止盈止损交易策略RSI与MACD结合EMA趋势和蜡烛形态识别-Multi-Confirmation-Dynamic-TP-SL-Trading-Strategy-RSI-and-MACD-Combined-with-EMA-Trend-and-Candlestick-Pattern-Recognition -> `fmz_488521_engulf_pinbar_ema50_rsi_macd_atr15_bracket_reversal`

- FMZ source id: 488521 (lineage).
- Source: https://www.fmz.com/strategy/488521 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-28 15:37:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Engulfing / pin-bar patterns with trend, RSI and MACD filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrMult` [1.5, 2.5] x `emaLength` [50, 100]: **4 trials**; RSI 14, MACD 12 / 26 / 9, ATR 14.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`trailing_stop_pending`
