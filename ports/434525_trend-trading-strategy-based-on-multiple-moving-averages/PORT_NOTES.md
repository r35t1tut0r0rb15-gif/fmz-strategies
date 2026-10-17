# #434525 Trend Trading Strategy Based on Multiple Moving Averages -> `fmz_434525_ema35_close_cross`

- FMZ source id: 434525 (lineage).
- Source: https://www.fmz.com/strategy/434525 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-07 10:50:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C68). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price against an average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [35, 20, 50]: **3 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
