# #489032 多指标动态交叉趋势跟踪量化策略分析-Multi-Indicator-Dynamic-Crossover-Trend-Following-Quantitative-Strategy-Analysis -> `fmz_489032_sma_5_20_cross_rsi_bb_atr_bracket`

- FMZ source id: 489032 (lineage).
- Source: https://www.fmz.com/strategy/489032 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 13:30:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | SMAs, RSI, bands and ATR multiples. |
| 3 | PASS | "Crypto Futures" in the title and the exchange pair only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [2.0, 1.0] x `tp_atr` [4.0, 2.0]: **4 trials**; defaults 2 / 4 (the source's); SMA 5 / 20, RSI 14 and BB
20 x 2 fixed.

## Ambiguities resolved

- The stored levels of the signal bar are re-issued unchanged: a fixed bracket (re-based on the fill).
- Close before entry: stop-and-reverse. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
