# #430669 Pivot Detector Oscillator Trend Trading Strategy -> `fmz_430669_pivot_detector_oscillator`

- FMZ source id: 430669 (lineage).
- Source: https://www.fmz.com/strategy/430669 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-31 14:47:05). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A rescaled RSI and a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ma` [200, 100] x `length_rsi` [14, 7]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
