# #458266 Adaptive Trend Following Strategy Based on Fibonacci Retracement -> `fmz_458266_close_range_fib_line_cross_point_bracket_reversal`

- FMZ source id: 458266 (lineage).
- Source: https://www.fmz.com/strategy/458266 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:14:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the point bracket as fractions of the fill |
| 2 | PASS | Retracement-line crossings with a point bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `tp_frac` [0.00238, 0.01] x `sl_frac` [0.00119, 0.005]: **8 trials**.

## Ambiguities resolved

- Points as fractions of 42000; bracket from the fill bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
