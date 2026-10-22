# #444018 基于多阶段布林带和MACD指标的量化交易策略Multi-Stage-Bollinger-Bands-MACD-Crossover-Signal-Quantitative-Trading-Strategy -> `fmz_444018_basis_cross_atr_away_macd_reversal`

- FMZ source id: 444018 (lineage).
- Source: https://www.fmz.com/strategy/444018 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 16:14:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Basis crossings an ATR away with a MACD filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `atr_length` [14, 7]: **4 trials**; the multiplier and the MACD fixed.

## Ambiguities resolved

- The band variants never fire, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
