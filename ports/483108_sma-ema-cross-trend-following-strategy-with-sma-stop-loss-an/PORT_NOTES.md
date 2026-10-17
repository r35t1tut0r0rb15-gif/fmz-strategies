# #483108 均线交叉趋势追踪策略结合SMA止损和重入场机制-EMA-Cross-Trend-Following-Strategy-with-SMA-Stop-Loss-and-Re-Entry-Mechanism -> `fmz_483108_ema50_150_cross_sma150_cut_reentry`

- FMZ source id: 483108 (lineage).
- Source: https://www.fmz.com/strategy/483108 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 16:59:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | qty = 1 quoted, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 30] x `slow` [150, 100]: **4 trials**; defaults 50 / 150 (the source's); the SMA close-out uses the slow
length (150 in the source).

## Ambiguities resolved

- `strategy.close("Buy Signal")` closes only a long opened under that id; a "Re-Buy Signal" long is held until the
  next short entry, but the flag is still set, as written.
- One position: same-side entries while held are ignored. Closes act on the position held at the bar's start and
  never undo an entry on that bar (as #430850); a close and a re-buy on one bar keep the long.
- REVERSAL INTENDED. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
