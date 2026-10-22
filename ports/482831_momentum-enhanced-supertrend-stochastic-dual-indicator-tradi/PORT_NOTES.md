# #482831 Momentum Enhanced SuperTrend Stochastic Dual Indicator Trading Strategy -> `fmz_482831_hl2_atr10_x3_band_state_stoch14_kd_cross_reversal`

- FMZ source id: 482831 (lineage).
- Source: https://www.fmz.com/strategy/482831 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:51:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band state with Stochastic crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [3.0, 2.0] x `atr_period` [10, 20]: **4 trials**; Stochastic 14 / 3 / 3, levels 20 / 80.

## Ambiguities resolved

- The band recursions are as written, not Pine's ta.supertrend. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
