# #439863 基于双EMA的趋势追踪策略Trend-Following-Strategy-Based-on-Dual-EMA -> `fmz_439863_a2mk_ema_support_line_cross`

- FMZ source id: 439863 (lineage).
- Source: https://www.fmz.com/strategy/439863 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-24 14:52:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema1` [34, 21] x `ema2` [13, 8]: **4 trials**.

## Ambiguities resolved

- Condition names swapped, orders as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
