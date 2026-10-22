# #468352 Multi Dimensional Mathematical Model Trading Strategy -> `fmz_468352_up_day_linreg14_over_ema50_long`

- FMZ source id: 468352 (lineage).
- Source: https://www.fmz.com/strategy/468352 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 17:36:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C208). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Up / down days with a regression-vs-EMA trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reg_len` [14, 30] x `ema_len` [50, 100]: **4 trials**.

## Ambiguities resolved

- The sigmoid repeats the change sign (as written). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
