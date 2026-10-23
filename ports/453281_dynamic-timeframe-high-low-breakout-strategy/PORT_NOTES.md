# #453281 Dynamic Timeframe High Low Breakout Strategy -> `fmz_453281_last_hour_break_prev_last_hour_close_points_reversal`

- FMZ source id: 453281 (lineage).
- Source: https://www.fmz.com/strategy/453281 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 17:01:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch C276). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; lower-time-frame values from each day's last hourly block |
| 2 | PASS | Last-hour breaks of the previous last-hour close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND453276. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`points_frac` [1.428571e-03, 5e-03, 1e-02]: **3 trials**; hourly blocks.

## Ambiguities resolved

- The "60" request is read as the day's last hourly block (no lookahead), reopened 2026-10-23.
- The points are price amounts (fractions of 42000). Call order on a two-way bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
