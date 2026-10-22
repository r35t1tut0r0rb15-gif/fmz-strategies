# #473385 多重均线交叉与RSI动态追踪止损量化交易策略-Multi-MA-Crossover-with-RSI-Dynamic-Trailing-Stop-Loss-Quantitative-Trading-Strategy -> `fmz_473385_sma9_21_cross_rsi_close_ratchet_reversal`

- FMZ source id: 473385 (lineage).
- Source: https://www.fmz.com/strategy/473385 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:10:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C218). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with RSI filters and close-based stops |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and levels are constants).

## Ambiguities resolved

- Level resets on exit tests also when flat, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
