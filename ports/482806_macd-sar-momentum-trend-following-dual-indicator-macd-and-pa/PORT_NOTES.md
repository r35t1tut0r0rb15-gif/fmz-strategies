# #482806 动量趋势跟踪型双指标MACD与抛物线SAR结合策略-Momentum-Trend-Following-Dual-Indicator-MACD-and-Parabolic-SAR-Combination-Strategy -> `fmz_482806_macd_signal_side_sar_side_always_in`

- FMZ source id: 482806 (lineage).
- Source: https://www.fmz.com/strategy/482806 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:45:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MACD and the parabolic SAR. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`af_max` [0.2, 0.1] x `slow` [26, 40]: **4 trials**; defaults 0.2 / 26 (the source's); MACD 12 / 9 and the SAR
start / step 0.02 fixed.

## Ambiguities resolved

- Every bar in a condition is an entry signal; the closes repeat the reversal. REVERSAL INTENDED (always in).
- `ta.sar` as #428699. Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
