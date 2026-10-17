# #488014 动态仓位与入场K线止损的EMA交叉策略-Dynamic-Position-Sizing-and-Entry-Candle-Stop-Loss-EMA-Crossover-Strategy -> `fmz_488014_ema10_20_cross_candle_low_stop`

- FMZ source id: 488014 (lineage).
- Source: https://www.fmz.com/strategy/488014 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 14:04:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop from the signal bar (moves marked). |
| 2 | PASS | EMAs and the signal bar's range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1000 / (close - low) quantity quoted; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [20, 30]: **4 trials**; defaults 10 / 20 (the source's).

## Trailing stop (mark `trailing_stop_pending`)

A later signal while held sets `entryCandleLow` to the new bar's low and re-issues `strategy.exit(stop = ...)`: the
stop moves. The port keeps the entry's stop (the signal bar's low, re-based on the fill).

## Ambiguities resolved

- The only exit is the stop, as written. Long only: opposite entries cannot occur. Stop module: `portfolio_kwargs` {}
  (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
