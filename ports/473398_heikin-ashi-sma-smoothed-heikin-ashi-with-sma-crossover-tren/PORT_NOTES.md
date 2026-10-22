# #473398 平滑型Heikin-Ashi结合SMA交叉趋势跟踪策略-Smoothed-Heikin-Ashi-with-SMA-Crossover-Trend-Following-Strategy -> `fmz_473398_smoothed_heikin_ashi_close_cross_sma44_reversal`

- FMZ source id: 473398 (lineage).
- Source: https://www.fmz.com/strategy/473398 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:39:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C218). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed Heikin-Ashi crossings of an SMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_long` [44, 100] x `smooth` [6, 12]: **4 trials**; the band fixed.

## Ambiguities resolved

- Band as a fraction of 42000 of the close. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
