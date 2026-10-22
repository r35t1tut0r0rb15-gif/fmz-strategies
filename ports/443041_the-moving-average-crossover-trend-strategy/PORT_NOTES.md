# #443041 The Moving Average Crossover Trend Strategy -> `fmz_443041_macd_cross_below_zero_long_any_short`

- FMZ source id: 443041 (lineage).
- Source: https://www.fmz.com/strategy/443041 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-28 17:55:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [12, 8] x `slow_length` [26, 50]: **4 trials**; the signal length fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
