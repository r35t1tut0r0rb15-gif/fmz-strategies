# #439625 The Gauss Wave Forecasting Strategy -> `fmz_439625_gauss_wave_forecast_open_side`

- FMZ source id: 439625 (lineage).
- Source: https://www.fmz.com/strategy/439625 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-22 12:37:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Gaussian filter forecast |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p` [20, 40, 10]: **3 trials**.

## Ambiguities resolved

- Version-2 local assignments do nothing, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
