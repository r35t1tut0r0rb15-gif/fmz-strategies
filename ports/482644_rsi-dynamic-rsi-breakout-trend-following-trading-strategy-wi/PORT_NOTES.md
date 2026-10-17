# #482644 动态RSI突破趋势跟踪交易策略结合风险收益比优化系统-Dynamic-RSI-Breakout-Trend-Following-Trading-Strategy-with-Risk-Reward-Ratio-Optimization-System -> `fmz_482644_rsi_turn_level_break_prev_bar_stop_rr4_2d`

- FMZ source id: 482644 (lineage).
- Source: https://www.fmz.com/strategy/482644 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-19 14:59:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-issued bracket fixed at entry (marked). |
| 2 | PASS | RSI turning points and the previous bar's range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `rr` [4, 2]: **4 trials**; defaults 14 / 4 (the source's).

## Trailing stop (mark `trailing_stop_pending`)

Every bar in the condition re-issues `strategy.exit` with that bar's previous low (high) and target, so the bracket
moves while held. The port keeps the entry's levels.

## Ambiguities resolved

- Two version lines (v6, then v5): v6 recorded. `rsi_prev_high` is the last RSI trough, `rsi_prev_low` the last peak.
- Both conditions on one bar: the short (written later) wins.
- A stop at or beyond the close emits no entry (zero-length, as L2 #491035).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Two-day bars: blocks of broker-day dates from
  1970-01-01 (decision owed, #426509).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
