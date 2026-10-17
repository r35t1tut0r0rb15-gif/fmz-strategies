# #482843 多重均线云层趋势交易策略-Multi-EMA-Cloud-Trend-Trading-Strategy -> `fmz_482843_ema9_21_cloud_long_1d`

- FMZ source id: 482843 (lineage).
- Source: https://www.fmz.com/strategy/482843 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:48:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 12] x `slow` [21, 50]: **4 trials**; defaults 9 / 21 (the source's); EMA 200 only plotted.

## Ambiguities resolved

- Every bullish bar is an entry signal. Long only: opposite entries cannot occur. No stops.
- Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
