# #440985 基于Stochastic指标的周期性期权交易策略Stochastic-Weekly-Options-Trading-Strategy -> `fmz_440985_stochastic_20_80_cross_reversal`

- FMZ source id: 440985 (lineage).
- Source: https://www.fmz.com/strategy/440985 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 15:14:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic level crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `low_level` [20, 30]: **4 trials**; high level = 100 - low.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
