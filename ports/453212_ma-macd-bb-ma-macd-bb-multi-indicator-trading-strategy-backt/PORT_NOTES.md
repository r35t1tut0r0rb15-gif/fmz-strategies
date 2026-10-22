# #453212 MA-MACD-BB多指标交易策略回测工具-MA-MACD-BB-Multi-Indicator-Trading-Strategy-Backtesting-Tool -> `fmz_453212_close_sma50_cross_long`

- FMZ source id: 453212 (lineage).
- Source: https://www.fmz.com/strategy/453212 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 09:49:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / SMA 50 crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [50, 20, 100]: **3 trials**.

## Ambiguities resolved

- Default MA / Long branch only. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
