# #478744 双均线-RSI多重信号趋势交易策略-Dual-Moving-Average-RSI-Multi-Signal-Trend-Trading-Strategy -> `fmz_478744_sma9_21_cross_rsi_filter_reversal`

- FMZ source id: 478744 (lineage).
- Source: https://www.fmz.com/strategy/478744 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 16:31:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; RSI 14 / 70 / 30.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
