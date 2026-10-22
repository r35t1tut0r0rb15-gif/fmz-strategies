# #446561 EMA双均线交叉趋势追踪策略EMA-Dual-Moving-Average-Crossover-Trend-Following-Strategy -> `fmz_446561_ema9_21_cross_long`

- FMZ source id: 446561 (lineage).
- Source: https://www.fmz.com/strategy/446561 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 16:44:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG446561. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
