# #439094 Momentum Breakout Optimization -> `fmz_439094_pmax_zlema_cross_long`

- FMZ source id: 439094 (lineage).
- Source: https://www.fmz.com/strategy/439094 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 16:44:30). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ZLEMA and ATR stop line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based quantity, capital, commission and slippage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND365691. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [3.0, 2.0] x `length` [10, 20]: **4 trials**; ATR 10 and hl2 fixed.

## Ambiguities resolved

- The sell order only flattens. Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
