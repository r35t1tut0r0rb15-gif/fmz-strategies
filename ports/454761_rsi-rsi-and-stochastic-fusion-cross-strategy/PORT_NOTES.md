# #454761 RSI与随机指标融合交叉策略-RSI-and-Stochastic-Fusion-Cross-Strategy -> `fmz_454761_rsi_stoch_stacked_turn_reversal`

- FMZ source id: 454761 (lineage).
- Source: https://www.fmz.com/strategy/454761 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 17:55:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked RSI / stochastic turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `k_len` [14, 7]: **4 trials**; the lines and smoothings fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
