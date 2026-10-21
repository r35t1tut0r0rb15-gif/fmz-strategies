# #437659 Momentum Bollinger Bands Breakout Strategy -> `fmz_437659_lower_band_cross_upper_flat`

- FMZ source id: 437659 (lineage).
- Source: https://www.fmz.com/strategy/437659 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 15:52:31). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [2.0, 1.5]: **4 trials**; filters off.

## Ambiguities resolved

- Short on the lower band as written; call-order fills. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
