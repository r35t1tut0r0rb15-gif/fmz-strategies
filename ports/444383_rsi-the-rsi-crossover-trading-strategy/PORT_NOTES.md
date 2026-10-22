# #444383 基于RSI-穿越交易策略The-RSI-Crossover-Trading-Strategy -> `fmz_444383_rsi19_35_70_cross_reversal`

- FMZ source id: 444383 (lineage).
- Source: https://www.fmz.com/strategy/444383 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-11 16:05:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [19, 14] x `oversold` [35, 30]: **4 trials**; the overbought level fixed.

## Ambiguities resolved

- Closes leave the reversals. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
