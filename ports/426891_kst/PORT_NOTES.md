# #426891 KST -> `fmz_426891_kst_cross`

- Source: https://www.fmz.com/strategy/426891 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-15 12:05:21). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

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

`scale` [0.5, 1.0, 1.5] (multiplies all eight ROC / SMA lengths) x `siglen` [9, 12]: **6 trials**, defaults 1.0 / 9 (the source's lengths).

## Ambiguities resolved

- ta.roc = 100 (close - close[n]) / close[n]; session / new-day variables unused.
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`
