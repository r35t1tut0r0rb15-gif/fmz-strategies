# #474874 均线交叉结合RSI趋势动量跟踪策略-Moving-Average-Crossover-with-RSI-Trend-Momentum-Tracking-Strategy -> `fmz_474874_sma9_21_cross_rsi50_reversal_bracket_pending`

- FMZ source id: 474874 (lineage).
- Source: https://www.fmz.com/strategy/474874 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 16:22:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with an RSI filter; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ma` [9, 5] x `long_ma` [21, 50]: **4 trials**; the bracket pending.

## Ambiguities resolved

- Per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
