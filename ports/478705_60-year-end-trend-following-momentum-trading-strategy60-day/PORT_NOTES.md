# #478705 年末趋势跟踪动量交易策略60日均线突破-Year-end-Trend-Following-Momentum-Trading-Strategy60-day-MA-Breakout -> `fmz_478705_close_cross_sma60_slope_dec31_exit_long`

- FMZ source id: 478705 (lineage).
- Source: https://www.fmz.com/strategy/478705 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 14:55:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with a slope filter and a calendar exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [60, 200] x `slope_len` [14, 5]: **4 trials**.

## Ambiguities resolved

- Year-end close on 31 December (UTC dates). Long only. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
