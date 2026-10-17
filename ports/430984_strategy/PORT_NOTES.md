# #430984 斐波那契回撤交易策略脚本 -> `fmz_430984_fib_retracement_cross_long`

- FMZ source id: 430984 (lineage).
- Source: https://www.fmz.com/strategy/430984 (PineScript v5, author Zer3192, FMZ last
  modified 2023-11-03 15:30:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Retracement fractions of a rolling range |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG430984. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 100] x `entry_fib` [0.618, 0.5]: **4 trials**; the exit level 0.236 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
