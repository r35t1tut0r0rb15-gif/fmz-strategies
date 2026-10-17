# #483518 基于RSI动量指标的自适应交易策略-Adaptive-Trading-Strategy-Based-on-RSI-Momentum-Indicator -> `fmz_483518_rsi_extremes_tight_pct_bracket`

- FMZ source id: 483518 (lineage).
- Source: https://www.fmz.com/strategy/483518 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:47:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (marked). |
| 2 | PASS | RSI and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.2, 1.0] x `tp_pct` [0.6, 3.0]: **4 trials**; defaults 0.2 / 0.6 (the source's); RSI 14 and 30 / 70 fixed.

## Trailing stop (mark `trailing_stop_pending`)

`longPrice = close` is read on every bar, so the stop and target are re-placed from the current close each day while
held. The port fixes them at the entry (fractions of the fill).

## Ambiguities resolved

- Every bar in the RSI zone is an entry signal (same-side ignored while held). REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4).
- Daily bars are broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`.
  FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
