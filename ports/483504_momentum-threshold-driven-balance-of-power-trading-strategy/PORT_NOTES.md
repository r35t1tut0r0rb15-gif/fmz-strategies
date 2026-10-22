# #483504 Momentum Threshold Driven Balance of Power Trading Strategy -> `fmz_483504_balance_of_power_0_8_cross_long`

- FMZ source id: 483504 (lineage).
- Source: https://www.fmz.com/strategy/483504 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:50:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Balance of Power level crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Leverage-5 quantity and 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_level` [0.8, 0.6] x `exit_level` [-0.8, -0.6]: **4 trials**.

## Ambiguities resolved

- The header's 1d wins over the title's 4H. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
