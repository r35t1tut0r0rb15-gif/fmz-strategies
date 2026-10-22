# #482889 Multi Indicator Crossover Trend Following Strategy with Fibonacci Retracement and Stop Loss Take Profit Optimization System -> `fmz_482889_ema9_21_cross_2_4pct_bracket_reversal`

- FMZ source id: 482889 (lineage).
- Source: https://www.fmz.com/strategy/482889 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:43:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | EMA crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [9, 5] x `slow_length` [21, 50]: **4 trials**; stop 2 %, target 4 %.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
