# #482886 高频量化多周期热图狙击策略-High-Frequency-Quantitative-Multi-Timeframe-Heatmap-Sniper-Strategy -> `fmz_482886_heatmap_band_cross_trend_reversal`

- FMZ source id: 482886 (lineage).
- Source: https://www.fmz.com/strategy/482886 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 16:35:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Smoothed rolling extremes and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sensitivity` [50, 20] x `lookback` [50, 20]: **4 trials**; defaults 50 / 50 (the source's); SMA 50 / 200 fixed.

## Ambiguities resolved

- The "week" / "month" MAs are 50 / 200 chart bars, as written; the max-trades input is unused.
- REVERSAL INTENDED; no exits or stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
