# #486567 Logarithmic Price Mean Reversion Dynamic Stop Loss Strategy -> `fmz_486567_log_zscore7_reversion_mean_target_vol_stop_flat`

- FMZ source id: 486567 (lineage).
- Source: https://www.fmz.com/strategy/486567 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-14 09:39:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based target and volatility stop |
| 2 | PASS | Log-price z-score mean reversion |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [7, 14] x `z_entry` [1.825, 1.5]: **4 trials**; stop z 2.125.

## Ambiguities resolved

- The flag loop and the volatility-moved stop are as written. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks

`none`
