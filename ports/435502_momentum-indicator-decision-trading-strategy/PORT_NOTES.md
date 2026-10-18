# #435502 Momentum Indicator Decision Trading Strategy -> `fmz_435502_smoothed_momentum_roc_band_stop`

- FMZ source id: 435502 (lineage).
- Source: https://www.fmz.com/strategy/435502 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 15:31:52). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | Smoothed momentum, a rate-of-change band and a percent stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430880. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.02, 0.05] x `length1` [31, 20]: **4 trials**; second smoothing 20, signal 9 and the ROC band fixed.

## Ambiguities resolved

- Stop fixed at the fill; target out of reach, dropped. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`coarse_bar_stop`
