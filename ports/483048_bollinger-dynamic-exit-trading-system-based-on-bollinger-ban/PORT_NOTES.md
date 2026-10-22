# #483048 基于Bollinger带策略应用的动态出场交易系统-Dynamic-Exit-Trading-System-Based-on-Bollinger-Bands-Application -> `fmz_483048_bb10_2_reentry_opposite_band_touch_exit_reversal`

- FMZ source id: 483048 (lineage).
- Source: https://www.fmz.com/strategy/483048 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:13:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band re-entries with band-touch exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1000 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- Band-touch exits act at the next open. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
