# #474062 Dual Timeframe Dynamic Support Trading System -> `fmz_474062_daily_band_cross_weekly_band_filter_long`

- FMZ source id: 474062 (lineage).
- Source: https://www.fmz.com/strategy/474062 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 16:44:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C221). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; completed weekly values |
| 2 | PASS | Daily band crossings filtered by the weekly band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_sma` [50, 100] x `long_sma` [20, 40]: **4 trials**; the EMAs one bar longer, as written.

## Ambiguities resolved

- Weekly values from the previous broker week. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
