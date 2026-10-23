# #435095 Volatility Price Channel Moving Average Trading Strategy -> `fmz_435095_linreg150_2sd_band_reentry_1m_reversal`

- FMZ source id: 435095 (lineage).
- Source: https://www.fmz.com/strategy/435095 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 11:44:15). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression band re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len5` [150, 60] x `multiplier` [2.0, 3.0]: **4 trials**.

## Ambiguities resolved

- Upper-band fall-back = long, as written. Volume not used (plot-only shadow line). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "regression_bands"`.

## Marks

`none`
