# #437663 Adaptive Botvenko Indicator Long Short Strategy -> `fmz_437663_botvenko_log_return_levels`

- FMZ source id: 437663 (lineage).
- Source: https://www.fmz.com/strategy/437663 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-04 16:09:30). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Log-return levels and EMA order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, margins and pyramiding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`nn` [60, 120] x `sell` [0.0065, 0.02]: **4 trials**; the other levels and EMA stack fixed.

## Ambiguities resolved

- Per-id closes in call order; window dropped. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
