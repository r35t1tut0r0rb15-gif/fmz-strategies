# #429960 Multiple Timeframe Trend Strategy -> `fmz_429960_three_timeframe_trend`

- FMZ source id: 429960 (lineage).
- Source: https://www.fmz.com/strategy/429960 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-23 16:56:52). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; higher-timeframe values from completed bars. |
| 2 | PASS | Stochastic levels and moving-average crosses. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_minutes` [5, 15] x `ma_trend` [50, 100]: **4 trials**; the x4 ladder, stochastic and SMA 7 / 21 fixed.

## Ambiguities resolved

- Higher timeframes = last completed bars (approximation stated). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
