# #426908 Fast and Slow Moving Average Crossover Strategy -> `fmz_426908_ema9_sma40_cross`

- Source: https://www.fmz.com/strategy/426908 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-12-01 14:57:24). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`fast` [5, 9] x `slow` [40, 60]: **4 trials**, defaults 9 / 40 (the source's).

## Ambiguities resolved

- strategy.entry reverses: REVERSAL INTENDED.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
