# #485292 Multi Timeframe Trend Recognition and Candlestick Pattern Trading Strategy -> `fmz_485292_engulf_rising_close_prev_low_stop_2r_long`

- FMZ source id: 485292 (lineage).
- Source: https://www.fmz.com/strategy/485292 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-07 09:57:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; previous-bar stop and 2R target as fractions of the fill |
| 2 | PASS | Engulfing candles on a rising close |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [2.0, 3.0, 1.5]: **3 trials**; stop at the previous bar's low.

## Ambiguities resolved

- The 15-minute security is the day's own close; the clock filters cannot fire on daily bars. A repeat signal's new levels are pending.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
