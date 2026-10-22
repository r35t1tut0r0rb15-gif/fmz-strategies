# #482644 动态RSI突破趋势跟踪交易策略结合风险收益比优化系统-Dynamic-RSI-Breakout-Trend-Following-Trading-Strategy-with-Risk-Reward-Ratio-Optimization-System -> `fmz_482644_rsi14_turn_value_break_prev_bar_stop_4r_reversal`

- FMZ source id: 482644 (lineage).
- Source: https://www.fmz.com/strategy/482644 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-19 14:59:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; previous-bar stop and 4R target as fractions of the fill |
| 2 | PASS | RSI breaks of its last turning values |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `rr` [4.0, 2.0]: **4 trials**; stop at the previous bar.

## Ambiguities resolved

- The turning-value names are swapped in the source, as written; the short wins when both hold.
- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
