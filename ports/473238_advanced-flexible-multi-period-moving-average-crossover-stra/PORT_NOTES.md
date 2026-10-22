# #473238 Advanced Flexible Multi Period Moving Average Crossover Strategy -> `fmz_473238_weekly_review_close_vs_weekly_ema30_long`

- FMZ source id: 473238 (lineage).
- Source: https://www.fmz.com/strategy/473238 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 15:18:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks |
| 2 | PASS | Weekly close-vs-EMA reviews |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [30, 10]: **2 trials**; the review frequency and MA method fixed.

## Ambiguities resolved

- Weekly EMA from the last completed broker week; first-bar buy as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
