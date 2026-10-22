# #439696 A Dual Moving Average Confirmation Advantage Line Strategy -> `fmz_439696_aroon_cross_lsma_confirm_long`

- FMZ source id: 439696 (lineage).
- Source: https://www.fmz.com/strategy/439696 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 10:49:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Aroon crossings and a regression line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [15, 25] x `lengthx` [20, 50]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
