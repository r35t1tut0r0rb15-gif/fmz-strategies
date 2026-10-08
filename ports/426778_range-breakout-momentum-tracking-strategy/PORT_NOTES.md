# #426778 Range Breakout Momentum Tracking Strategy -> `fmz_426778_follow_line`

- Source: https://www.fmz.com/strategy/426778 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-14 15:10:46). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_period` [14, 21] x `bb_dev` [1.0, 1.5] x `atr_period` [5, 10]: **8 trials**, defaults 21 / 1.0 / 5 (the source's); ATR filter on.

## Ambiguities resolved

- ta.atr(5) inside the if-blocks: each call site's RMA advances only on its own bars (Pine per-call-site history; FMZ may differ: decision owed).
- Range filter and Hull suite only plot; Pine population stdev.
- FREQ = "4h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`none`
