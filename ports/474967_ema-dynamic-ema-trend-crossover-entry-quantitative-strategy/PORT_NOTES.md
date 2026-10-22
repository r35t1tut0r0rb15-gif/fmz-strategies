# #474967 EMA趋势交叉动态入场量化策略-Dynamic-EMA-Trend-Crossover-Entry-Quantitative-Strategy -> `fmz_474967_ema14_100_cross_long`

- FMZ source id: 474967 (lineage).
- Source: https://www.fmz.com/strategy/474967 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:55:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [14, 9] x `long_len` [100, 50]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
