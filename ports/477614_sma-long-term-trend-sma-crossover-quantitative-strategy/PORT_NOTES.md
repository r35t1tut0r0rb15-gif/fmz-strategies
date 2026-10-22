# #477614 长期趋势SMA均线交叉量化策略-Long-term-Trend-SMA-Crossover-Quantitative-Strategy -> `fmz_477614_sma5_20_cross_long`

- FMZ source id: 477614 (lineage).
- Source: https://www.fmz.com/strategy/477614 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 17:01:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 10] x `slow` [20, 50]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
