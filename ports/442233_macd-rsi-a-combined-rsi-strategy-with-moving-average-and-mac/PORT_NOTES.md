# #442233 移动平均线与MACD结合的RSI指标交易策略A-Combined-RSI-Strategy-with-Moving-Average-and-MACD -> `fmz_442233_ema3_30_cross_ema50_side_reversal`

- FMZ source id: 442233 (lineage).
- Source: https://www.fmz.com/strategy/442233 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 14:28:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C153). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings on the EMA 50 side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema3_length` [3, 9] x `ema30_length` [30, 50]: **4 trials**; EMA 50 fixed.

## Ambiguities resolved

- The exit closes never act (ids not entered). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
