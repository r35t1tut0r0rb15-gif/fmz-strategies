# #433434 基于RSI指标的量化交易策略Quantitative-Trading-Strategy-Based-on-RSI-Indicator -> `fmz_433434_planb_rsi_regime`

- FMZ source id: 433434 (lineage).
- Source: https://www.fmz.com/strategy/433434 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-27 16:02:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 1000 cash quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sell_level` [90, 80] x `window` [6, 12]: **4 trials**; RSI 14, drop 65, buy level 50 and bounce 2 fixed.

## Ambiguities resolved

- A bar with both signals ends short. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
