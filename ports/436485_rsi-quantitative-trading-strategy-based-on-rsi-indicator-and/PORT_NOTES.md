# #436485 基于RSI指标和移动平均线的量化交易策略Quantitative-Trading-Strategy-Based-on-RSI-Indicator-and-Moving-Average -> `fmz_436485_sma_cross_rsi_timing`

- FMZ source id: 436485 (lineage).
- Source: https://www.fmz.com/strategy/436485 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-25 11:40:36). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C89). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossings and RSI timing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [11, 8] x `slow` [82, 60]: **4 trials**; RSI 14 and its limits fixed.

## Ambiguities resolved

- Flags followed inside simulate; orders in call order. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
