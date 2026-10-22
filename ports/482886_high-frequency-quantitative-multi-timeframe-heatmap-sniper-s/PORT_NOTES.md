# #482886 High Frequency Quantitative Multi Timeframe Heatmap Sniper Strategy -> `fmz_482886_smoothed_50bar_low_high_cross_sma50_200_trend_reversal`

- FMZ source id: 482886 (lineage).
- Source: https://www.fmz.com/strategy/482886 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 16:35:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed channel crossings with an SMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [50, 100] x `sensitivity` [50, 20]: **4 trials**; SMA 50 / 200.

## Ambiguities resolved

- REVERSAL INTENDED, no other exit. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
