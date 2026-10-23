# #426323 Quantitative Trend Trading Strategy Using Polynomial Regression -> `fmz_426323_index_sqrt_regression_turning_point_vwap_angle_close_bracket_reversal`

- FMZ source id: 426323 (lineage).
- Source: https://www.fmz.com/strategy/426323 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-11 09:04:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based target / stop |
| 2 | PASS | Regression-curve turning points with a VWAP-angle filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = round(equity / close) and the commented strategy() stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [26, 30] x `angulo` [26.8, 10.0]: **4 trials**; p 4, SL 1.4 %, TP 5.6 %.

## Ambiguities resolved

- The regression and the VWAP angle are kept as written (data-start and price-unit dependent: weird case).
- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "regression_channel"`.

## Marks

`none`
