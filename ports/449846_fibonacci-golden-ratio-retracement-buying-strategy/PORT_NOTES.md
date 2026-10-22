# #449846 Fibonacci Golden Ratio Retracement Buying Strategy -> `fmz_449846_swing_line_fib_level_close_long`

- FMZ source id: 449846 (lineage).
- Source: https://www.fmz.com/strategy/449846 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 17:08:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Swing-line and Fibonacci-level closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`price_len` [50, 100] x `swing` [1, 5]: **4 trials**; the Fibonacci ratios fixed.

## Ambiguities resolved

- Swing line from the bar itself (length 1). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
