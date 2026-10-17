# #482645 多指标动态趋势交叉量化交易策略-Multi-Indicator-Dynamic-Trend-Crossover-Quantitative-Trading-Strategy -> `fmz_482645_macd_ema_joint_cross_rsi_always_in`

- FMZ source id: 482645 (lineage).
- Source: https://www.fmz.com/strategy/482645 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 15:01:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs, MACD and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 34]: **4 trials**; defaults 9 / 21 (the source's); MACD 12 / 26 / 9 and RSI 14 (30 / 70)
fixed.

## Ambiguities resolved

- Both crosses must fall on the same bar (as written). REVERSAL INTENDED (always in). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
