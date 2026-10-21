# #437656 Quant Lights Moving Average Trend Tracking Optimization Strategy -> `fmz_437656_stochastic_ott_cross`

- FMZ source id: 437656 (lineage).
- Source: https://www.fmz.com/strategy/437656 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 15:44:23). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic against its own trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_k` [250, 100] x `smooth_k` [50, 20]: **4 trials**; OTT 3 / 0.618 fixed.

## Ambiguities resolved

- nz-seeded VIDYA as written; OTT two bars back. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
