# #449553 RSI与双EMA交叉信号量化策略-RSI-and-Dual-EMA-Crossover-Signal-Quantitative-Strategy -> `fmz_449553_rsi_extreme_beyond_ema100_ema20low_reversal`

- FMZ source id: 449553 (lineage).
- Source: https://www.fmz.com/strategy/449553 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-26 17:36:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI extremes beyond two EMAs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `ema_close` [100, 200]: **4 trials**; the EMA of lows and the levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
