# #442010 Dual Moving Average Intelligent Tracking Trading Strategy -> `fmz_442010_ott_var_cross_long`

- FMZ source id: 442010 (lineage).
- Source: https://www.fmz.com/strategy/442010 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-18 15:58:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | OTT crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG442010. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10] x `percent` [1.0, 2.0]: **4 trials**.

## Ambiguities resolved

- VAR nz resets as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
