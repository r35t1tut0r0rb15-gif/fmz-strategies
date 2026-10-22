# #477587 Advanced Fibonacci Retracement Trend Following and Reversal Trading Strategy -> `fmz_477587_fib_range50_618_382_cross_level_close_reversal`

- FMZ source id: 477587 (lineage).
- Source: https://www.fmz.com/strategy/477587 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 15:43:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fibonacci retracement crossings with level closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [50, 100, 20]: **3 trials**; the four levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
