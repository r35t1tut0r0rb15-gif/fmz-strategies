# #432099 Multi Timeframe Trend Tracking Strategy -> `fmz_432099_three_way_trend_agreement`

- FMZ source id: 432099 (lineage).
- Source: https://www.fmz.com/strategy/432099 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-14 14:29:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA, MACD-ratio and RSI comparisons |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [10, 20] x `np_len` [50, 25]: **4 trials**; EMA 12 / 21, WMA 10 and RSI 14 / 50 fixed.

## Ambiguities resolved

- Close conventions as stated. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
