# #483088 多重时间框架趋势跟踪策略结合动态仓位管理和ATR止盈止损系统-Multi-Timeframe-Trend-Following-Strategy-with-Dynamic-Position-Sizing-and-ATR-Based-Take-Profit-Stop-Loss-System -> `fmz_483088_macd_cross_ema7_90_h8_filter_atr_bracket_1h_reversal`

- FMZ source id: 483088 (lineage).
- Source: https://www.fmz.com/strategy/483088 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:02:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | MACD crossings in an EMA 7 / 90 trend with an 8-hour filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Trend-strength quantity and cash size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 2.0] x `tp_atr` [3.0, 2.0]: **4 trials**; EMA 7 / 90, MACD 12 / 26 / 9, 8-hour EMA 7 / SMA 50.

## Ambiguities resolved

- 8-hour values from completed blocks; shorts close at once (long levels), as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
