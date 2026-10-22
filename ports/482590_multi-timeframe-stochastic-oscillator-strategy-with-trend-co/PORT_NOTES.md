# #482590 Multi Timeframe Stochastic Oscillator Strategy with Trend Confirmation Trading System -> `fmz_482590_stoch15_extreme_cross_swing5_pct_bracket_reversal`

- FMZ source id: 482590 (lineage).
- Source: https://www.fmz.com/strategy/482590 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 10:53:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C246). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the signal close as fractions of the fill |
| 2 | PASS | Stochastic extreme crossings with a swing check |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [3.7, 2.0] x `tp_pct` [1.8, 4.0]: **4 trials**; Stoch 15 / 4 / 5, 85 / 15, swing 5.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop_pending`
