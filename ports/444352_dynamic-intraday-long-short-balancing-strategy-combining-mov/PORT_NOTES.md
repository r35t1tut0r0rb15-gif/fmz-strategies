# #444352 Dynamic Intraday Long Short Balancing Strategy Combining Moving Average and Supertrend -> `fmz_444352_daily_3m_supertrend_change_30m_macd_reversal`

- FMZ source id: 444352 (lineage).
- Source: https://www.fmz.com/strategy/444352 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-11 11:33:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 3- and 30-minute values end with the daily bar |
| 2 | PASS | Day-to-day changes of the 3-minute SuperTrend direction with a MACD filter |
| 3 | PASS | Exchange pair in the header only; the Asia/Kolkata timezone input is never used. |
| 4 | DONE | The 100 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [1.0, 3.0] x `atr_period` [7, 14]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- Clock branches never act on daily bars; last 3-/30-minute bar of each broker day. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
