# #443119 基于EMA均线和RSI指标的量化交易策略EMA-and-RSI-Quantitative-Trading-Strategy -> `fmz_443119_ema50_sma100_cross_rsi_exits`

- FMZ source id: 443119 (lineage).
- Source: https://www.fmz.com/strategy/443119 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-29 13:52:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA / SMA crossings with RSI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG443119. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `overbought` [70, 80]: **4 trials** (oversold = 100 - overbought); the MA lengths fixed.

## Ambiguities resolved

- Closes act on held ids. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
