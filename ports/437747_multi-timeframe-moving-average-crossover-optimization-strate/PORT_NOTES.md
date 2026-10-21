# #437747 Multi Timeframe Moving Average Crossover Optimization Strategy -> `fmz_437747_ma_direction_state_trail`

- FMZ source id: 437747 (lineage).
- Source: https://www.fmz.com/strategy/437747 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-05 12:05:42). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | ADAPT | Tick trail -> ATR multiple and a fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick trail inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427510. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `trail_k` [0.04, 1.0]: **4 trials**; SMA type, smoothing 2 and activation 0.0005 fixed.

## Ambiguities resolved

- Tick trail as a house volatility trail (stated approximation); VWMA type left out. REVERSAL INTENDED. Marks coarse_bar_stop, trailing_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`coarse_bar_stop, trailing_stop`
