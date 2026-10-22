# #439717 基于MACD和RSI的趋势追踪交易策略Trend-Following-Trading-Strategy-Based-on-MACD-and-RSI -> `fmz_439717_macd5_13_rsi_filter_candle_close`

- FMZ source id: 439717 (lineage).
- Source: https://www.fmz.com/strategy/439717 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-23 12:03:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings, RSI and candle crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 12] x `slow` [13, 26]: **4 trials**; signal 5 and RSI 14 fixed.

## Ambiguities resolved

- Closes after entries. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
