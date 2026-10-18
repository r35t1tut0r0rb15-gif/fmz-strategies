# #435771 Trend Following Regression Trading Strategy Based on Linear Regression and Moving Average -> `fmz_435771_sma_cross_regression_filter`

- FMZ source id: 435771 (lineage).
- Source: https://www.fmz.com/strategy/435771 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 17:34:29). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average cross and a regression level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent stop and target inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [14, 30, 50]: **3 trials**.

## Ambiguities resolved

- Regression read at i = n; exits never fire. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
