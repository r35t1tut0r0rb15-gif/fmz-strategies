# #449958 Stochastic Oscillator and Moving Average Strategy -> `fmz_449958_stoch_extreme_sma9_slope_2pct_stop_1m_reversal`

- FMZ source id: 449958 (lineage).
- Source: https://www.fmz.com/strategy/449958 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 16:45:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry (re-sent levels marked) |
| 2 | PASS | Stochastic extremes with an SMA slope filter, percent stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The qty 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND449526. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `sl` [0.02, 0.01]: **4 trials**; the smoothing, levels and the SMA fixed.

## Ambiguities resolved

- Closes never act; stop from the fill. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop_pending`
