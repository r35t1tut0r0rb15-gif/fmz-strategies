# #433394 基于KDJ和RSI的买卖点策略KDJ-RSI-Crossover-Buy-Sell-Signals-Strategy -> `fmz_433394_kdj_rsi_cross`

- FMZ source id: 433394 (lineage).
- Source: https://www.fmz.com/strategy/433394 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-27 10:57:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator crosses and levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kdj_len` [9, 14] x `rsi_fast` [6, 9]: **4 trials**; signal 3 and RSI 12 / 24 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
