# #443108 基于移动平均线交叉和K线形态的比特币scalping策略Bitcoin-Scalping-Strategy-Based-on-Moving-Average-Crossover-and-Candlestick-Patterns -> `fmz_443108_sma9_15_cross_steep_slope_body_long`

- FMZ source id: 443108 (lineage).
- Source: https://www.fmz.com/strategy/443108 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-29 12:01:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the per-bar bracket described (pending) |
| 2 | ADAPT | Price-unit slope angle -> scaled to the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG443108. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `angle` [30, 60]: **4 trials**; the slow SMA fixed.

## Ambiguities resolved

- Angle scaled to the close; re-sent bracket pending (no exit). Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
