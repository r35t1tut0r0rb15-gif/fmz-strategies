# #482444 多重支撑阻力位叠加动量反转交易策略-Multi-Level-Support-Resistance-Momentum-Reversal-Trading-Strategy -> `fmz_482444_rsi_extreme_fib_range_levels_long`

- FMZ source id: 482444 (lineage).
- Source: https://www.fmz.com/strategy/482444 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 14:49:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Retracement fractions of a range and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 20 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7]: **2 trials**; default 14 (the source's); the 70 / 30 levels and the Fibonacci fractions fixed.

## Ambiguities resolved

- The range is the expanding min / max of up-closes from the first bar (past only; start-dependent, as written).
  The "or" tests reduce to close > fib 61.8 (buy) and close < fib 38.2 (sell). Pivots only feed drawings.
- The close acts on the position held at the bar's start and never undoes an entry on that bar (#430850).
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
