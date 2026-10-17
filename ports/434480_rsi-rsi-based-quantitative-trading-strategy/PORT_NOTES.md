# #434480 基于RSI的量化交易策略RSI-Based-Quantitative-Trading-Strategy -> `fmz_434480_dual_rsi_cross_signal_exits`

- FMZ source id: 434480 (lineage).
- Source: https://www.fmz.com/strategy/434480 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-06 17:17:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI crosses and percent exit signals |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slen` [55, 14] x `tp` [0.009, 0.03]: **4 trials**; RSI 126 and the 3 % exit fixed.

## Ambiguities resolved

- EMA-smoothed RSIs; exits as close-based signals against the signal close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
