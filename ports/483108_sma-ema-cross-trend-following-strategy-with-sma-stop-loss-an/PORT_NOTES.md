# #483108 均线交叉趋势追踪策略结合SMA止损和重入场机制-EMA-Cross-Trend-Following-Strategy-with-SMA-Stop-Loss-and-Re-Entry-Mechanism -> `fmz_483108_ema50_150_cross_sma150_close_stop_reentry_reversal`

- FMZ source id: 483108 (lineage).
- Source: https://www.fmz.com/strategy/483108 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 16:59:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based SMA stop |
| 2 | PASS | EMA crossings with an SMA stop and a re-entry |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [150, 100]: **4 trials**; the SMA stop uses the slow length.

## Ambiguities resolved

- The SMA stop closes only the "Buy Signal" long, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
