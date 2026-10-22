# #442553 基于MA线的趋势追踪策略Trend-Following-Strategy-Based-on-MA-Lines -> `fmz_442553_close_sma60_cross_fill_ratio_exits`

- FMZ source id: 442553 (lineage).
- Source: https://www.fmz.com/strategy/442553 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 17:24:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C158). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings; closes against the fill price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [60, 30] x `stop_ratio` [0.1, 0.05]: **4 trials**; the 300 % target fixed.

## Ambiguities resolved

- One ratio formula for both sides, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
