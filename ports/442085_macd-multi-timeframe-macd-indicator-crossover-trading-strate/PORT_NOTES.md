# #442085 多时间轴MACD指标交叉交易策略Multi-timeframe-MACD-Indicator-Crossover-Trading-Strategy -> `fmz_442085_close_vs_wma25_ema50_ema100_reversal`

- FMZ source id: 442085 (lineage).
- Source: https://www.fmz.com/strategy/442085 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-19 11:03:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C150). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against three averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wma_length` [25, 50] x `ema2_length` [100, 200]: **4 trials**; EMA 50 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
