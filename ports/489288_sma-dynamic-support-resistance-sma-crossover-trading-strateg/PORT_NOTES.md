# #489288 动态支撑阻力SMA交叉黄金交易策略三重确认与风险管理优化框架-Dynamic-Support-Resistance-SMA-Crossover-Trading-Strategy-Triple-Confirmation-with-Risk-Management-Optimization-Framework -> `fmz_489288_sma_10_20_cross_retest_swing_bracket`

- FMZ source id: 489288 (lineage).
- Source: https://www.fmz.com/strategy/489288 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 10:51:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (mark). |
| 2 | PASS | Moving averages and swing levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing` [10, 20] x `rr` [2.0, 3.0]: **4 trials**; defaults 10 / 2 (the source's); SMA 10 / 20 and the 3-bar
breakout / retest windows fixed.

## Moving bracket (rule 2, mark `trailing_stop_pending`)

The exits are issued every bar from the current 10-bar extreme and close, so stop and target move. Fixed at the
signal bar here (re-based on the fill); zero-risk signals emit no entry.

## Ambiguities resolved

- Every condition bar is an entry; entries reverse. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
