# #484912 多重斐波那契优化时间入场策略-Multi-Fibonacci-Optimal-Time-Entry-Strategy -> `fmz_484912_ote_fib705_cross`

- FMZ source id: 484912 (lineage).
- Source: https://www.fmz.com/strategy/484912 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-05 09:45:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Retracement levels of rolling extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50]: **2 trials**; default 20 (the source's only trading input).

## Ambiguities resolved

- The swing tests include the current bar (the latest bar making a 20-bar extreme), as written; the levels are na
  until both swings exist. No exit other than the opposite entry: REVERSAL INTENDED. Daily bars are broker days;
  FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "fibonacci_retracement"`.

## Marks

`none`
