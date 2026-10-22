# #477951 自适应双向EMA趋势交易系统与反向交易优化策略-Adaptive-Dual-Direction-EMA-Trend-Trading-System-with-Reverse-Trade-Optimization-Strategy -> `fmz_477951_timed_ema5_40_side_opposite_ema5_10_cross_reversal`

- FMZ source id: 477951 (lineage).
- Source: https://www.fmz.com/strategy/477951 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 15:24:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Timed EMA-side trades with opposite crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`interval_min` [30, 60] x `main_long` [40, 20]: **4 trials**; opposite EMA 5 / 10, delay 1 min, window 10:30-15:00 UTC.

## Ambiguities resolved

- UTC window, no DST; a same-bar crossing replaces the main entry. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
