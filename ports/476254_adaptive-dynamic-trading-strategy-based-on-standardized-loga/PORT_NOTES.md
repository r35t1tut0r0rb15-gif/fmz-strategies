# #476254 Adaptive Dynamic Trading Strategy Based on Standardized Logarithmic Returns -> `fmz_476254_log_return_zscore50_extreme_reversal`

- FMZ source id: 476254 (lineage).
- Source: https://www.fmz.com/strategy/476254 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 14:39:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C230). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar bracket described (pending) |
| 2 | PASS | Log-return z-score extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored; risk percentage unused. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [50, 20] x `threshold` [2.0, 1.5]: **4 trials**; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket from the latest close kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks

`trailing_stop_pending`
