# #440979 双重指标的Stochastic-RSI和EMA交易策略Dual-Indicator-Stochastic-RSI-and-EMA-Trading-Strategy -> `fmz_440979_close_stoch_dip_ema_trend_long`

- FMZ source id: 440979 (lineage).
- Source: https://www.fmz.com/strategy/440979 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-04 15:00:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C142). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic of the close and EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_length` [14, 7] x `ema1_period` [55, 34]: **4 trials**; EMA 200 and the levels fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
