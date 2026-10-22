# #489198 Multi Momentum Indicator Trend Tracking Quantitative Trading Strategy -> `fmz_489198_ema9_21_cross_rsi50_macd_reversal`

- FMZ source id: 489198 (lineage).
- Source: https://www.fmz.com/strategy/489198 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 16:19:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C270). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with RSI and MACD confirmation |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emaFastLength` [9, 5] x `emaSlowLength` [21, 50]: **4 trials**; RSI 14, MACD 12 / 26 / 9.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
