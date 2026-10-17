# #482820 多重移动平均线与布林带交叉期权量化交易策略-Multi-Moving-Average-and-Bollinger-Bands-Crossover-Options-Quantitative-Trading-Strategy -> `fmz_482820_sma5_11_cross_bb_outside_sma55_atr_bracket`

- FMZ source id: 482820 (lineage).
- Source: https://www.fmz.com/strategy/482820 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:53:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (marked). |
| 2 | PASS | Three SMAs, Bollinger bands and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 2.5] x `tp_mult` [3.0, 5.0]: **4 trials**; defaults 1.5 / 3 (the source's); SMA 5 / 11 / 55,
BB 22 / 1.5 and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

`strategy.exit` runs on every bar from the current close and ATR, so stop and target move with the price. The port
fixes them at the entry's signal bar (re-based on the fill).

## Ambiguities resolved

- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850);
  `simulate()` mirrors the house bracket from the fill (as #430254) so a close after a stop exit is not emitted.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`trailing_stop_pending`
