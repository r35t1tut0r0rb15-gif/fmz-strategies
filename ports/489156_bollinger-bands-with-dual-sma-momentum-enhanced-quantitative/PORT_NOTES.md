# #489156 布林带结合快速与慢速移动平均线的多维趋势强化量化交易策略-Bollinger-Bands-with-Dual-SMA-Momentum-Enhanced-Quantitative-Trading-Strategy -> `fmz_489156_bb_upper_breakout_sma_trend_long`

- FMZ source id: 489156 (lineage).
- Source: https://www.fmz.com/strategy/489156 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 11:28:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bands and SMAs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted (commission and slippage are costs). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `slow_sma` [45, 100]: **4 trials**; defaults 21 / 45 (the source's); multiplier 2, SMA 6 fixed.

## Ambiguities resolved

- The basis defaults to SMA; the VWMA option (volume) is not used (check 8). Long only. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
