# #474030 DPO-EMA趋势交叉量化策略研究-DPO-EMA-Trend-Crossover-Quantitative-Strategy-Research -> `fmz_474030_dpo24_ema4_cross_long`

- FMZ source id: 474030 (lineage).
- Source: https://www.fmz.com/strategy/474030 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 14:57:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | DPO crossings of its EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (the lengths are constants).

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
