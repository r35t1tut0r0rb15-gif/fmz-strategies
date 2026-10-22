# #477977 多重EMA交叉趋势跟踪量化交易策略-Multi-EMA-Crossover-Trend-Following-Quantitative-Trading-Strategy -> `fmz_477977_ema10_50_cross_ema200_trend_reversal`

- FMZ source id: 477977 (lineage).
- Source: https://www.fmz.com/strategy/477977 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 16:33:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C238). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings in an EMA 200 trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ema` [10, 20] x `medium_ema` [50, 100]: **4 trials**; EMA 200.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
