# #431971 Dual Reversal Entry Strategy -> `fmz_431971_rb_reversal_tabs`

- FMZ source id: 431971 (lineage).
- Source: https://www.fmz.com/strategy/431971 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-13 17:56:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD sign and stochastic levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_period` [70, 35] x `k_period` [30, 15]: **4 trials**; MACD 12 / 26 / 9 and levels 30 / 70 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
