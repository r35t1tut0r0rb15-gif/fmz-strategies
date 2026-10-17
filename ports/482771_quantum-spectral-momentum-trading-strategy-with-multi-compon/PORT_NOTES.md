# #482771 基于量子谱分析的多维动量交易策略-Quantum-Spectral-Momentum-Trading-Strategy-with-Multi-Component-Analysis -> `fmz_482771_composite_outlook_index_bar_extreme_stop`

- FMZ source id: 482771 (lineage).
- Source: https://www.fmz.com/strategy/482771 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bar-extreme stops as exit signals (marked). |
| 2 | PASS | Z-scores, EMA ratios and bar extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [50, 100] x `band` [20, 10]: **4 trials** (band 20 = the source's 70 / 30); defaults 50 / 20; EMA 20 / 50
and the weights 20 / 30 / 20 / 10 fixed.

## Trailing stop (mark `trailing_stop_pending`)

While the index is below 50 the long's `strategy.exit` is re-issued with the stop at the current bar's low (short:
above 50, the high), so the level moves bar by bar after the entry. The house bracket is fixed at the fill and
cannot carry it. `simulate()` keeps the resting order and emits an exit signal on the bar whose low (high) reaches
it, filled at the next open (one bar after Pine's stop fill).

## Ambiguities resolved

- An exit placed while its entry is not open is not carried into a later trade (Pine may attach it to the next
  entry of that id).
- A bar that reaches the stop and also signals: the opposite signal reverses; a same-side signal is dropped.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`trailing_stop_pending`
