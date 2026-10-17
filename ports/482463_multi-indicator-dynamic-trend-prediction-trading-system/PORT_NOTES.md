# #482463 多指标动态趋势预测交易系统-Multi-Indicator-Dynamic-Trend-Prediction-Trading-System -> `fmz_482463_rsi_stoch_extremes_daily_pivot_filter`

- FMZ source id: 482463 (lineage).
- Source: https://www.fmz.com/strategy/482463 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:22:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the daily pivots without look-ahead. |
| 2 | PASS | RSI, a stochastic and confirmed pivots. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `stoch_len` [14, 21]: **4 trials**; defaults 14 / 14 (the source's); levels 70 / 30, 80 / 20 and
daily pivots 3 / 3 fixed.

## Ambiguities resolved

- Daily pivots (non-na only on the confirming day) from the last completed broker day as of each bar's close (house
  rule, #490787); `nz()` turns the other days into 0, so the long filter always passes and the short filter needs a
  pivot high confirmed the previous day (as written). Strict pivots (#430850).
- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850).
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
