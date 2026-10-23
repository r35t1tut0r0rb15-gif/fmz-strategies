# #482900 多指标趋势跟踪策略结合ATR动态止盈止损-Multi-Indicator-Trend-Following-Strategy-with-ATR-Dynamic-Stop-Loss-Take-Profit -> `fmz_482900_ema9_21_cross_rsi_volume_candle_break_atr_bracket_reversal`

- FMZ source id: 482900 (lineage).
- Source: https://www.fmz.com/strategy/482900 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:27:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | EMA crossings confirmed by RSI, volume and a candle break |
| 3 | PASS | Exchange pair in the header only (TRB_USDT). |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 2.0] x `tp_atr` [3.0, 2.0]: **4 trials**; EMA 9 / 21, RSI 14, volume SMA 20, ATR 14.

## Ambiguities resolved

- No trailing stop (no offset). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
