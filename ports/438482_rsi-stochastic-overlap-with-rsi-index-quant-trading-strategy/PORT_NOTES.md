# #438482 双均线叠加RSI指标的量化交易策略Stochastic-Overlap-with-RSI-Index-Quant-Trading-Strategy -> `fmz_438482_stoch_extreme_cross_rsi`

- FMZ source id: 438482 (lineage).
- Source: https://www.fmz.com/strategy/438482 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-12 13:57:36). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic crossings and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_k` [14, 9] x `os_level` [20, 30]: **4 trials**; overbought = 100 - oversold; D 3, smooth 3, RSI 14 at 50 / 60 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
