# #442108 Absolute Momentum Indicator Strategy -> `fmz_442108_cmo_abs_band_state_reversal`

- FMZ source id: 442108 (lineage).
- Source: https://www.fmz.com/strategy/442108 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-19 14:13:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C151). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Absolute CMO bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430117. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [9, 14] x `top_band` [70, 60]: **4 trials**; low band 20 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
