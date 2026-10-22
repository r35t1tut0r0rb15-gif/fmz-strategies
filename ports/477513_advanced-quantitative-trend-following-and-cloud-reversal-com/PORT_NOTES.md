# #477513 Advanced Quantitative Trend Following and Cloud Reversal Composite Trading Strategy -> `fmz_477513_ema9_21_crossup_sma_ichimoku_crossdown_reversal`

- FMZ source id: 477513 (lineage).
- Source: https://www.fmz.com/strategy/477513 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 10:56:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar bracket described (pending) |
| 2 | PASS | EMA cross-ups and SMA-Ichimoku cross-downs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ema` [9, 5] x `kijun` [26, 50]: **4 trials**; long EMA 21, Tenkan 9, span B 52; the per-bar bracket pending.

## Ambiguities resolved

- SMA-based lines and span A = SMA 2 of the sum, as written. Per-bar bracket pending (trailing_stop_pending).
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`trailing_stop_pending`
