# #482426 多周期高斯通道结合StochRSI趋势跟踪策略-Multi-Period-Gaussian-Channel-with-StochRSI-Trend-Following-Strategy -> `fmz_482426_gaussian144_breakout_stochrsi_extreme_long`

- FMZ source id: 482426 (lineage).
- Source: https://www.fmz.com/strategy/482426 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 13:50:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C243). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Gaussian-channel breakouts with a Stochastic RSI extreme filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 250 % of equity stored, not ported; commission not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sampling_period` [144, 89] x `multiplier` [1.414, 2.0]: **4 trials**; poles 4, Stoch RSI 14 / 14 / 3.

## Ambiguities resolved

- Filter state starts at 0, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_band"`.

## Marks

`none`
