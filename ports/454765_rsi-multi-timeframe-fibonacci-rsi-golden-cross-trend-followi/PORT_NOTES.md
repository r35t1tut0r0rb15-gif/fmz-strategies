# #454765 多周期斐波那契RSI黄金交叉趋势跟踪量化交易策略-Multi-Timeframe-Fibonacci-RSI-Golden-Cross-Trend-Following-Quantitative-Trading-Strategy -> `fmz_454765_golden_cross_range_mid_rsi_exit_reversal`

- FMZ source id: 454765 (lineage).
- Source: https://www.fmz.com/strategy/454765 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 18:07:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Golden / death crosses with a range-midpoint side and RSI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [50, 20] x `long_len` [200, 100] x `fib_len` [50, 100]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- Call order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
