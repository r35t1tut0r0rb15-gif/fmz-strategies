# #489007 Multi EMA Trend Reversal Trading Strategy -> `fmz_489007_ema10_20_30_perfect_order_onset_break_exit_reversal`

- FMZ source id: 489007 (lineage).
- Source: https://www.fmz.com/strategy/489007 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 10:02:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA stack onsets with a stack-break exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`aPeriod` [10, 5] x `cPeriod` [30, 50]: **4 trials**; EMA 20.

## Ambiguities resolved

- The flag loop is as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
