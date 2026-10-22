# #491505 EMA Crossover Dynamic Trailing Stop Loss Strategy -> `fmz_491505_ema9_21_cross_close_trail1pct_reversal`

- FMZ source id: 491505 (lineage).
- Source: https://www.fmz.com/strategy/491505 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-21 15:53:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested trail |
| 2 | PASS | EMA crossings with a close-based trail |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trailStopPercent` [1.0, 3.0] x `emaLength2` [21, 50]: **4 trials**; EMA 9.

## Ambiguities resolved

- The close trail is followed in a loop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
