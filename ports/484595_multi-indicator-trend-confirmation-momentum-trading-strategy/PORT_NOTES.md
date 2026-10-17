# #484595 多指标趋势确认动量交易策略-Multi-Indicator-Trend-Confirmation-Momentum-Trading-Strategy -> `fmz_484595_ema20_50_cross_filters_long`

- FMZ source id: 484595 (lineage).
- Source: https://www.fmz.com/strategy/484595 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 10:35:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs and oscillators. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**; defaults 20 / 50 (the source's); EMA 200, RSI 14 and MACD
12 / 26 / 9 fixed.

## Ambiguities resolved

- The Fibonacci levels and EMA 100 are drawn only. Long only, exit on the bearish mirror: opposite entries cannot
  occur. Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
