# #483064 基于高斯通道与随机RSI的多重指标自适应交易策略-Multi-Indicator-Adaptive-Trading-Strategy-Based-on-Gaussian-Channel-and-Stochastic-RSI -> `fmz_483064_gaussian4_144_channel_upper_break_stochrsi_long`

- FMZ source id: 483064 (lineage).
- Source: https://www.fmz.com/strategy/483064 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:28:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C256). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Gaussian channel breakout with Stochastic RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [144, 72] x `mult` [1.414, 2.0]: **4 trials**; 4 poles, Stochastic RSI 14 / 14 / 3 / 3.

## Ambiguities resolved

- Default modes (reduced lag, fast response) off. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
