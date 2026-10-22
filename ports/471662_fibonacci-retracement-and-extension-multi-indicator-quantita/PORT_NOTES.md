# #471662 Fibonacci Retracement and Extension Multi Indicator Quantitative Trading Strategy -> `fmz_471662_range10_retracement_side_ema20_50_trend_reversal`

- FMZ source id: 471662 (lineage).
- Source: https://www.fmz.com/strategy/471662 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 10:51:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range-level closes in an EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`range_len` [10, 20] x `fast` [20, 10] x `slow` [50, 100]: **8 trials**.

## Ambiguities resolved

- Any-level loop = the outermost level (as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
