# #474980 Intelligent Volatility Range Trading Strategy Combining Bollinger Bands and SuperTrend -> `fmz_474980_bb20_retest_supertrend_dir_line_cross_exit_reversal`

- FMZ source id: 474980 (lineage).
- Source: https://www.fmz.com/strategy/474980 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 11:47:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band re-tests with supertrend filters and line-cross closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_bb` [20, 50] x `factor` [3.0, 2.0]: **4 trials**; ATR 10.

## Ambiguities resolved

- Direction tests as written (Pine direction 1 = down-trend). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
