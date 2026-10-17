# #483089 动态突破下降楔形趋势线量化交易策略-Dynamic-Breakout-Falling-Wedge-Trendline-Quantitative-Trading-Strategy -> `fmz_483089_falling_wedge_breakout_long`

- FMZ source id: 483089 (lineage).
- Source: https://www.fmz.com/strategy/483089 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:02:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Pivot trendlines and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot_bars` [5, 3] x `tp_pct` [20.0, 10.0]: **4 trials**; defaults 5 / 20 (the source's); left = right pivot bars;
the 2 % stop fixed.

## Trailing stop (mark `trailing_stop_pending`)

A later signal while held re-places the stop and target from the new close. The port keeps the entry's bracket.

## Ambiguities resolved

- Pivots are strict extremes confirmed `rightBars` later (as #430850).
- `ta.crossover` sits inside the wedge block, so it compares with the values of the last bar on which the block ran
  (per-call history), as written.
- Long only: opposite entries cannot occur. Stop module: `portfolio_kwargs` {} (D4).
- Broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
