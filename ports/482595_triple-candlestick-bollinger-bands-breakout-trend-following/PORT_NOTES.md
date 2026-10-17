# #482595 基于布林带突破的三连阳阳线高点趋势跟踪策略-Triple-Candlestick-Bollinger-Bands-Breakout-Trend-Following-Strategy-with-High-Low-Point-Confirmation -> `fmz_482595_three_strong_closes_outside_bb_1r_flat`

- FMZ source id: 482595 (lineage).
- Source: https://www.fmz.com/strategy/482595 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-19 11:05:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | Bollinger bands, candle shape and the setup's extreme. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 1.5] x `rr` [1.0, 2.0]: **4 trials**; defaults 2 / 1 (the source's); BB 20 fixed.

## Ambiguities resolved

- Bracket fractions of the signal close, re-based on the fill; a stop not below (above) the close emits no entry.
- Entries from flat only: `simulate()` mirrors the house bracket from the fill (as #430254).
- Stop module: `portfolio_kwargs` {} (D4). FREQ = "12h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop`
