# #482863 五分钟开盘突破ATR动态止盈止损量化交易策略-Five-Minute-Opening-Breakout-Strategy-with-Dynamic-ATR-Based-Stop-Loss-and-Take-Profit -> `fmz_482863_open_0930utc_5min_candle_break_atr_range_bracket_reversal`

- FMZ source id: 482863 (lineage).
- Source: https://www.fmz.com/strategy/482863 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:33:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; opening-candle bracket as fractions of the fill |
| 2 | PASS | Opening-candle breakouts with an ATR stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_factor` [1.0, 2.0] x `tp_factor` [1.5, 1.0]: **4 trials**; ATR 14, capture 09:30 UTC.

## Ambiguities resolved

- The capture time is 09:30 UTC (the exchange time zone of the header), not New York.
- The exit re-sent with the current ATR is fixed at the signal bar; pending. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "opening_range"`.

## Marks

`trailing_stop_pending`
