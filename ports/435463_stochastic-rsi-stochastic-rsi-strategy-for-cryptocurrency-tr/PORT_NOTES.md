# #435463 基于Stochastic-RSI的数字货币交易策略Stochastic-RSI-Strategy-for-Cryptocurrency-Trading -> `fmz_435463_stoch_rsi_vigor_events`

- FMZ source id: 435463 (lineage).
- Source: https://www.fmz.com/strategy/435463 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 10:08:14). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator events |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`per` [5, 10] x `length_rsi` [14, 21]: **4 trials**; stochastic 14, K and D smoothing 3 fixed.

## Ambiguities resolved

- Latest-event side; swma weights. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
