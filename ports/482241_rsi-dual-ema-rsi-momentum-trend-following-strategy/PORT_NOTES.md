# #482241 双均线-RSI动量趋势跟踪策略-Dual-EMA-RSI-Momentum-Trend-Following-Strategy -> `fmz_482241_ema6_82_cross_close_direction_rsi_reversal`

- FMZ source id: 482241 (lineage).
- Source: https://www.fmz.com/strategy/482241 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-17 10:51:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C243). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a close-direction and RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_short` [6, 12] x `ema_long` [82, 50]: **4 trials**; RSI 14 / 70 / 22.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
