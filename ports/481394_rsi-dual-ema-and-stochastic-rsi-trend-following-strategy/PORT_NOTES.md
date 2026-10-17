# #481394 双均线与随机RSI趋势跟踪策略-Dual-EMA-and-Stochastic-RSI-Trend-Following-Strategy -> `fmz_481394_ema9_21_cross_stoch_rsi_extreme_always_in`

- FMZ source id: 481394 (lineage).
- Source: https://www.fmz.com/strategy/481394 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 16:56:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs and a stochastic RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`os` [20, 30] (overbought = 100 - os) x `slow` [21, 50]: **4 trials**; defaults 20 / 21 (the source's 20 / 80 and
21); EMA 9, RSI 14, stochastic 14 / 3 fixed.

## Ambiguities resolved

- The closes repeat the reversal. REVERSAL INTENDED (always in). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
