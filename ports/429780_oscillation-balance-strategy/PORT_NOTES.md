# #429780 Oscillation Balance Strategy -> `fmz_429780_projected_balance_of_power`

- FMZ source id: 429780 (lineage).
- Source: https://www.fmz.com/strategy/429780 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-20 17:03:08). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle-body ratios only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed 1 / 0 quantities stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`proj_lag` [2, 1] x `slowest` [18, 30]: **4 trials**; EMAs 3 / 6 / 9 / 12 fixed.

## Ambiguities resolved

- Zero-quantity short read as a close of the long. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
