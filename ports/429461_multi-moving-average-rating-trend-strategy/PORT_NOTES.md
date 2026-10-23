# #429461 Multi Moving Average Rating Trend Strategy -> `fmz_429461_eighty_two_ma_vote_rating_thresholds_reversal`

- FMZ source id: 429461 (lineage).
- Source: https://www.fmz.com/strategy/429461 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 13:11:25). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average vote thresholds |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rating_entry` [0.95, 0.8] x `rating_exit` [0.75, 0.9]: **4 trials**.

## Ambiguities resolved

- Every MA as its source function (zero-start recursions kept). Volume = broker tick volume (VWMA votes).
- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_rating"`.

## Marks

`none`
