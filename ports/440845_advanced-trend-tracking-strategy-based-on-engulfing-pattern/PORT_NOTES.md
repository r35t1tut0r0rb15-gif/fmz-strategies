# #440845 Advanced Trend Tracking Strategy Based on Engulfing Pattern and Quantitative Indicators -> `fmz_440845_confirmed_fractal_entries`

- FMZ source id: 440845 (lineage).
- Source: https://www.fmz.com/strategy/440845 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 16:48:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots confirmed from past bars |
| 2 | PASS | Swing pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars` [2, 3]: **2 trials**; the same left and right length.

## Ambiguities resolved

- Swing high buys as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`none`
