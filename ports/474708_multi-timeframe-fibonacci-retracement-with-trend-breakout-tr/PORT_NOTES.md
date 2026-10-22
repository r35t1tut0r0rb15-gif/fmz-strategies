# #474708 Multi Timeframe Fibonacci Retracement with Trend Breakout Trading Strategy -> `fmz_474708_fib618_786_4h_range_candles_bracket_reversal`

- FMZ source id: 474708 (lineage).
- Source: https://www.fmz.com/strategy/474708 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 17:32:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C223). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; completed 4-hour values; signal-bar bracket as fractions of the fill |
| 2 | PASS | Retracement-level candles with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fib1` [0.618, 0.5] x `sl_pct` [0.01, 0.005]: **4 trials**; fib2 0.786, risk-reward 2, timeframe 240.

## Ambiguities resolved

- 4-hour bars UTC-aligned; extremes over 2-minute samples, as written. Repeat re-sends not followed. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`trailing_stop_pending`
