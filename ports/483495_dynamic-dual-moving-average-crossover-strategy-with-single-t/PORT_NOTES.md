# #483495 双均线动态交叉策略之指数移动均线交叉执行单次交易系统-Dynamic-Dual-Moving-Average-Crossover-Strategy-with-Single-Trade-Execution-System-using-Exponential-Moving-Averages -> `fmz_483495_ema9_21_cross_long_only`

- FMZ source id: 483495 (lineage).
- Source: https://www.fmz.com/strategy/483495 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-24 09:15:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 12] x `slow` [21, 26]: **4 trials**; defaults 9 / 21 (the source's).

## Ambiguities resolved

- The unused "Strategy Timeframe" input is ignored; FREQ = "1h" from the header.
- Long only, one trade at a time: the raw crosses are emitted (same-side and flat exits are ignored by the engine).
  Opposite entries cannot occur. No stops.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
