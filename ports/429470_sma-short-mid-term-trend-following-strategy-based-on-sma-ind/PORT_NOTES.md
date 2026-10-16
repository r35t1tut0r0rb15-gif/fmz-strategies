# #429470 基于SMA指标的短中期趋势跟踪策略Short-Mid-Term-Trend-Following-Strategy-Based-on-SMA-Indicators -> `fmz_429470_sma3_50_cross_long`

- FMZ source id: 429470 (lineage).
- Source: https://www.fmz.com/strategy/429470 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 14:27:10). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average crosses only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 10-unit quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [3, 5] x `slow` [50, 30]: **4 trials**; exit SMA 40 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
