# #435707 超级趋势-LSMA-多头策略Super-Trend-LSMA-Long-Strategy -> `fmz_435707_supertrend_lsma_long`

- FMZ source id: 435707 (lineage).
- Source: https://www.fmz.com/strategy/435707 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 10:43:14). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend and a regression average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `lengthx` [101, 50]: **4 trials**; ATR 14 fixed.

## Ambiguities resolved

- LSMA = end of the regression line; date window dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
