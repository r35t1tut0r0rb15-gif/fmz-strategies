# #481370 Adaptive-Bollinger-Bands-Trend-Following-Strategy-with-Multi-Level-Risk-Management-自适应布林带趋势跟踪策略与多层风险管理系统 -> `fmz_481370_bb14_reversal_candle_ema80_slope_point_stop_bars10_reversal`

- FMZ source id: 481370 (lineage).
- Source: https://www.fmz.com/strategy/481370 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 15:14:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving trailing stop described (pending) |
| 2 | PASS | Band reversal candles with an EMA slope filter, point stop and time exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 300 / 1000 $ inputs stored (TP off). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars_till_close` [10, 5] x `sl_frac` [7.14286e-03, 0.02]: **4 trials**; BB 14 / 1.5, EMA 80; the trailing stop pending.

## Ambiguities resolved

- The 300-$ stop is a price amount (fraction of 42000). The bar count runs through a reversal, as written. The basis-armed trailing stop is pending.
- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
