# #489031 自动化斐波那契回撤交易系统策略-Automated-Fibonacci-Retracement-Trading-System-Strategy -> `fmz_489031_fib_618_382_cross_bracket`

- FMZ source id: 489031 (lineage).
- Source: https://www.fmz.com/strategy/489031 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 13:25:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | Range fractions and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1 %-risk quantity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 50] x `sl_pct` [1.0, 2.0]: **4 trials**; defaults 20 / 1 (the source's); TP 2 % and the levels fixed.

## Ambiguities resolved

- The swing window includes the current bar. REVERSAL INTENDED. Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`coarse_bar_stop`
