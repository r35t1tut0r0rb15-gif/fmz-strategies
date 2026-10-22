# #473412 多重指数均线交叉战略结合交易量ATR动态止损优化策略-Multi-Exponential-Moving-Average-Crossover-Strategy-with-Volume-Based-ATR-Dynamic-Stop-Loss-Optimization -> `fmz_473412_ema10_39_cross_ema73_daily143_atr_bracket_reversal`

- FMZ source id: 473412 (lineage).
- Source: https://www.fmz.com/strategy/473412 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 17:06:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the daily EMA from the block's last day; signal-bar ATR bracket |
| 2 | PASS | EMA crossings with trend filters and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and multiples are constants).

## Ambiguities resolved

- Daily EMA from the 2-day block's last broker day. REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
