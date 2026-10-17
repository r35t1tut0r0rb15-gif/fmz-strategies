# #483064 基于高斯通道与随机RSI的多重指标自适应交易策略-Multi-Indicator-Adaptive-Trading-Strategy-Based-on-Gaussian-Channel-and-Stochastic-RSI -> `fmz_483064_gaussian_channel_breakout_stochrsi_long`

- FMZ source id: 483064 (lineage).
- Source: https://www.fmz.com/strategy/483064 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:28:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A recursive filter channel scaled by filtered true range; a stochastic RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [144, 100] x `mult` [1.414, 2.0]: **4 trials**; defaults 144 / 1.414 (the source's); 4 poles, reduced lag and
fast response off, stochastic RSI 3 / 14 / 14 fixed.

## Ambiguities resolved

- `f_filt9x` is the n-pole recursion with binomial weights; `nz()` = 0 for missing history and the missing first true
  range, as written.
- Every bar in the condition is an entry signal. Long only: opposite entries cannot occur. No stops.
- Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
