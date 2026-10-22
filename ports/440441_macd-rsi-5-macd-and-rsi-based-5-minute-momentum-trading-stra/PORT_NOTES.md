# #440441 基于MACD和RSI的5分钟动量交易策略MACD-and-RSI-Based-5-Minute-Momentum-Trading-Strategy -> `fmz_440441_rsi_macd_momentum_one_bar_short`

- FMZ source id: 440441 (lineage).
- Source: https://www.fmz.com/strategy/440441 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-30 15:59:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI and MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `rsi_oversold` [30, 40]: **4 trials**; overbought = 100 - oversold; MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Close tests from the same close: long never, short always. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
