# #473397 基于Hull移动平均线的反射型EMA趋势判定策略-Reflected-EMA-Trend-Determination-Strategy-Based-on-Hull-Moving-Averages -> `fmz_473397_reflected_hull_peak_trough_reversal`

- FMZ source id: 473397 (lineage).
- Source: https://www.fmz.com/strategy/473397 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:35:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C218). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Peak / trough reversals of a reflected Hull line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`correction_pct` [0.04, 1.0] x `smooth` [2, 5]: **4 trials**; the HMA lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
