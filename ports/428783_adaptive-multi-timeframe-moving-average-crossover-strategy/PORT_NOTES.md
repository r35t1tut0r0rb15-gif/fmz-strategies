# #428783 Adaptive Multi Timeframe Moving Average Crossover Strategy -> `fmz_428783_macd_hist_thrust`

- FMZ source id: 428783 (lineage).
- Source: https://www.fmz.com/strategy/428783 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-09 14:56:37). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | The price-unit tolerance -> an ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() line stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tol_atr` [0.02, 0.1] x `lookback` [6, 10]: **4 trials**; EMAs 21 / 55 / 9 and ATR 14 fixed.

## Ambiguities resolved

- Tolerance as an ATR multiple (criterion 2). A same-bar long and short: the long is kept.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
