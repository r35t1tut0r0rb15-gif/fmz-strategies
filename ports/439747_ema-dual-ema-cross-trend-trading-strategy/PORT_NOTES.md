# #439747 基于EMA指标的双线交叉趋势交易策略Dual-EMA-Cross-Trend-Trading-Strategy -> `fmz_439747_ema30_reclaim_ema60_stop_long`

- FMZ source id: 439747 (lineage).
- Source: https://www.fmz.com/strategy/439747 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-23 14:43:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C124). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | EMA crossings and levels from the signal bar |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema30_length` [30, 20] x `ema60_length` [60, 100]: **4 trials**; 10-bar high target fixed.

## Ambiguities resolved

- Bracket from the signal bar. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
