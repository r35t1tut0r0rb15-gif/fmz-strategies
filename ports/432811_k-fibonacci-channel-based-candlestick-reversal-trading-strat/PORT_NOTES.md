# #432811 基于斐波那契通道的K线反转策略Fibonacci-Channel-Based-Candlestick-Reversal-Trading-Strategy -> `fmz_432811_fibonacci_keltner_outer_breakout`

- FMZ source id: 432811 (lineage).
- Source: https://www.fmz.com/strategy/432811 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-21 17:24:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR bands, an RSI filter and WMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fib` [4.236, 2.618] x `ma_len` [233, 89]: **4 trials**; KC 89 x 2 and RSI 14 fixed.

## Ambiguities resolved

- close_all after the entries leaves the bar flat. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
