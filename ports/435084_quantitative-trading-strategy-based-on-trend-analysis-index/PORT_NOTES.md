# #435084 Quantitative Trading Strategy Based on Trend Analysis Index -> `fmz_435084_trend_analysis_index`

- FMZ source id: 435084 (lineage).
- Source: https://www.fmz.com/strategy/435084 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-12 10:40:52). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A percent slope range |
| 3 | PASS |  |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`avg_len` [28, 14] x `top` [0.11, 0.3]: **4 trials**; TAI 5 and the low band 0.02 fixed.

## Ambiguities resolved

- No bar size (bar_size_pending). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "slope_momentum"`.

## Marks

`bar_size_pending`
