# #473246 Double Seven Strategy Trend Following and Mean Reversion Dual Optimization Trading SystemDouble Seven Strategy -> `fmz_473246_connors_double_seven_long`

- FMZ source id: 473246 (lineage).
- Source: https://www.fmz.com/strategy/473246 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 15:41:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | 7-day closing extremes in an uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [7, 5] x `ma_len` [200, 100]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
