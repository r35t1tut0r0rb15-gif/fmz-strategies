# #488034 马德里带状RSI增强型多时框EMA趋势策略-Madrid-Ribbon-RSI-Enhanced-Multi-Timeframe-EMA-Trend-Strategy -> `fmz_488034_madrid_ribbon_rsi_bracket`

- FMZ source id: 488034 (lineage).
- Source: https://www.fmz.com/strategy/488034 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-24 15:52:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal close (re-placement marked). |
| 2 | PASS | Moving-average slopes and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash quantity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`use_ema` [True, False] x `sl_pct` [1.0, 2.0]: **4 trials**; defaults EMA / 1 % (the source's); the 18 ribbon MAs 5-90
against MA 100, counts 13 / 9, RSI 14 (30 / 70) and the 0.5 % target fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the target and stop from the new close (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The colour chain is evaluated in the source's order (a flat MA below the reference is red). REVERSAL INTENDED.
  Stop module: `portfolio_kwargs` {} (D4). Daily bars are broker days; FREQ = "1D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_ribbon"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
