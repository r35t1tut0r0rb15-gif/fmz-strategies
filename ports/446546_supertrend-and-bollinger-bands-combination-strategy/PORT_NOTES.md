# #446546 Supertrend and Bollinger Bands Combination Strategy -> `fmz_446546_supertrend_line_cross_outside_bands_reversal`

- FMZ source id: 446546 (lineage).
- Source: https://www.fmz.com/strategy/446546 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-29 15:18:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend-line crossings outside the bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `bb_len` [20, 50]: **4 trials**; the ATR length and the band deviation fixed.

## Ambiguities resolved

- na seeds as written. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
