# #482881 多重技术指标趋势跟踪通道突破交易策略与K线形态过滤系统-Multi-Technical-Indicator-Trend-Following-Channel-Breakout-Trading-Strategy-with-Candlestick-Pattern-Filtering-System -> `fmz_482881_keltner_breakout_engulfing_volume_rolling_atr_bracket_1h_reversal`

- FMZ source id: 482881 (lineage).
- Source: https://www.fmz.com/strategy/482881 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:30:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar re-sent bracket followed in the signals |
| 2 | PASS | Keltner breakouts confirmed by engulfing candles on volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.5, 2.0] x `tp_atr` [2.0, 3.0]: **4 trials**; EMA 20, ATR 14, SL 1.5 ATR.

## Ambiguities resolved

- Re-sent bracket followed at the next open. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_breakout"`.

## Marks

`trailing_stop_pending`
