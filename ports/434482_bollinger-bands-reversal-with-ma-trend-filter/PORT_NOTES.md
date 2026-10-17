# #434482 Bollinger Bands Reversal with MA Trend Filter -> `fmz_434482_bollinger_ma_double_cross_long`

- FMZ source id: 434482 (lineage).
- Source: https://www.fmz.com/strategy/434482 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-06 17:34:51). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band and average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [20, 40] x `ma_len` [50, 100]: **4 trials**; 2 deviations fixed.

## Ambiguities resolved

- Same-bar double crosses, as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
