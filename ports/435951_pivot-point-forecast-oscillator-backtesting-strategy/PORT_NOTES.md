# #435951 Pivot Point Forecast Oscillator Backtesting Strategy -> `fmz_435951_chande_forecast_sign`

- FMZ source id: 435951 (lineage).
- Source: https://www.fmz.com/strategy/435951 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-20 13:44:26). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length` [14, 21]: **4 trials**.

## Ambiguities resolved

- linreg end value; state changes only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
