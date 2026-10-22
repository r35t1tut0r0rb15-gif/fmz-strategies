# #442207 Trend Following Strategy Based on Smoothed Deviation -> `fmz_442207_smoothed_cost_deviation_sign_reversal`

- FMZ source id: 442207 (lineage).
- Source: https://www.fmz.com/strategy/442207 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 11:15:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed deviation sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_term` [5, 10] x `long_term` [20, 50]: **4 trials**; smoothing 5, threshold 0 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
