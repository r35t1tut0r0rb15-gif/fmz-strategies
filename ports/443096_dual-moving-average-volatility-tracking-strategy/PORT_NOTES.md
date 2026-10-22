# #443096 Dual Moving Average Volatility Tracking Strategy -> `fmz_443096_golden_cross_cmo_var_filter_long`

- FMZ source id: 443096 (lineage).
- Source: https://www.fmz.com/strategy/443096 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-29 11:15:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Golden crosses with a CMO-weighted line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**; the VAR length fixed.

## Ambiguities resolved

- VAR as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
