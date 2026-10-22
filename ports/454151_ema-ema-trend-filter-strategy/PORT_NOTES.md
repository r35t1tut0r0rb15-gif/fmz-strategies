# #454151 EMA趋势过滤策略EMA-Trend-Filter-Strategy -> `fmz_454151_ema9_21_cross_ema200_side_ema14_slope_exit_reversal`

- FMZ source id: 454151 (lineage).
- Source: https://www.fmz.com/strategy/454151 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-14 15:51:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a trend filter and a slope exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50] x `trend_len` [200, 100]: **8 trials**; the EMA 14 fixed.

## Ambiguities resolved

- Closes before entries. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
