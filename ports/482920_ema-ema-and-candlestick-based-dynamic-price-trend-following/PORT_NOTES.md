# #482920 基于EMA和蜡烛图的动态价格跟踪趋势交易策略-EMA-and-Candlestick-Based-Dynamic-Price-Trend-Following-Strategy -> `fmz_482920_pin_engulf_ema8_21_trend_reversal`

- FMZ source id: 482920 (lineage).
- Source: https://www.fmz.com/strategy/482920 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 17:43:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C253). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle patterns with an EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 5] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED, no other exit. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
