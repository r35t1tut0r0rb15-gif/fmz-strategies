# #442625 多时间框架RSI交易策略Multi-Timeframe-RSI-Trading-Strategy -> `fmz_442625_three_tf_rsi_order_daily_reversal`

- FMZ source id: 442625 (lineage).
- Source: https://www.fmz.com/strategy/442625 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 12:24:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; lower-time-frame values ending with the daily bar |
| 2 | PASS | Multi-time-frame RSI ordering |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND438798. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `floor` [30, 40]: **4 trials** (the 4-hour floor; the ceiling is 100 - floor).

## Ambiguities resolved

- Lower-time-frame values as the day's last bars. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
