# #449508 MACD-V和斐波那契多时间框架动态止盈策略-MACD-V-and-Fibonacci-Multi-Timeframe-Dynamic-Take-Profit-Strategy -> `fmz_449508_macdv_5m_fib_30m_from_flat_atr_stop`

- FMZ source id: 449508 (lineage).
- Source: https://www.fmz.com/strategy/449508 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-25 11:28:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C179). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 5- and 30-minute values end with the hourly bar; the trailing exit not ported (mark) |
| 2 | PASS | MACD-V momentum against Fibonacci levels with a tick stop as an ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1000 % of equity size and margins stored; the commission is a cost, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [13.33, 5.0] x `fib_lookback` [9, 20]: **4 trials**; the MACD-V lengths and the two time frames fixed.

## Ambiguities resolved

- Tick stop as 13.33 ATR(14); trailing exit pending; last 5- / 30-minute bar of each hour. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`trailing_stop_pending`
