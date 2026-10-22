# #477596 Multi Timeframe Heikin Ashi Moving Average Trend Following Trading System -> `fmz_477596_last3h_ha_close_vs_daily_ha_ema30_reversal`

- FMZ source id: 477596 (lineage).
- Source: https://www.fmz.com/strategy/477596 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:20:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 3-hour value from completed blocks of past days |
| 2 | PASS | Heikin-Ashi close against its slow EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [30, 60, 15]: **3 trials**; the 3-hour block fixed.

## Ambiguities resolved

- The 3-hour value is the chart day's last 3-hour block (from the broker-day start). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi"`.

## Marks

`none`
