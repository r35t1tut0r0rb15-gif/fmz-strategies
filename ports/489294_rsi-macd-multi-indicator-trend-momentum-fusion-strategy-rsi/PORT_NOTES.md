# #489294 多指标趋势动量融合策略-RSI-MACD-双重超趋势跟踪系统-Multi-Indicator-Trend-Momentum-Fusion-Strategy-RSI-MACD-Dual-Supertrend-Tracking-System -> `fmz_489294_rsi_macd_dual_supertrend_bracket`

- FMZ source id: 489294 (lineage).
- Source: https://www.fmz.com/strategy/489294 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:03:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (mark). |
| 2 | PASS | Oscillators, ATR bands and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_low` [35, 45] x `tp_atr` [2.5, 1.5]: **4 trials**; defaults 35 / 2.5 (the source's); RSI 14 (65), MACD
5 / 13 / 9, ATR 14, SL 1 ATR and SuperTrend 9 x 2 / 7 fixed.

## Moving bracket (rule 2, mark `trailing_stop_pending`)

`strategy.exit(stop = close -+ 1 ATR, limit = close +- 2.5 ATR, trail_points = 1 ATR)` is issued on every bar, so the
levels follow the close. Fixed at the signal bar here. `trail_points` without `trail_offset` is inert in Pine.

## Ambiguities resolved

- The source's own SuperTrend function, as written. The break-even level is never used.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
