# #453276 Percentage Threshold Quantitative Trading Strategy -> `fmz_453276_prev_close_pct_range_break_reversal`

- FMZ source id: 453276 (lineage).
- Source: https://www.fmz.com/strategy/453276 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 16:41:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C192). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Previous-close range breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND453276. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pct` [1.04, 2.0, 0.5]: **3 trials**.

## Ambiguities resolved

- Call order on a two-way bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
