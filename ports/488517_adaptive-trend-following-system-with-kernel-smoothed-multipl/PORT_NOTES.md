# #488517 Adaptive Trend Following System with Kernel Smoothed Multiple Moving Averages -> `fmz_488517_kernel_ma_ribbon_order_rsi7_strength_confirm4_reversal`

- FMZ source id: 488517 (lineage).
- Source: https://www.fmz.com/strategy/488517 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-28 15:13:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C266). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the close-ratchet trail pending |
| 2 | PASS | Kernel-MA ribbon order with RSI and trend-strength filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity and commission 0.02 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`maCrossoversRequired` [3, 4] x `trendConfirmationPeriod` [4, 2]: **4 trials**; kernels and RSI as written.

## Ambiguities resolved

- The close-ratchet trail is pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_ribbon"`.

## Marks

`trailing_stop_pending`
