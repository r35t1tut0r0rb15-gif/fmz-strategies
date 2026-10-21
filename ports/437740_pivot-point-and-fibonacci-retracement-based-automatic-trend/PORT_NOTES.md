# #437740 Pivot Point and Fibonacci Retracement Based Automatic Trend Following Strategy -> `fmz_437740_abcd_pivot_fib_bracket`

- FMZ source id: 437740 (lineage).
- Source: https://www.fmz.com/strategy/437740 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 11:34:17). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Pivot ratios and structure levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10]: **2 trials**; the ratio windows and the 1.5x target fixed.

## Ambiguities resolved

- Pivot bookkeeping as written; structure bracket as distances from the signal close. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
