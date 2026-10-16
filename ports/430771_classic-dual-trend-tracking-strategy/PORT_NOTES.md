# #430771 Classic Dual Trend Tracking Strategy -> `fmz_430771_daily_pivot_pullbacks`

- FMZ source id: 430771 (lineage).
- Source: https://www.fmz.com/strategy/430771 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-01 16:54:29). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; completed daily values. |
| 2 | PASS | Pivot levels of the previous day. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`r2_mult` [1.0, 0.5]: **2 trials**; R2 / S2 = pivot +- r2_mult x (H - L) of the previous day (1.0 the source's).

## Ambiguities resolved

- Previous broker day's pivots. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
