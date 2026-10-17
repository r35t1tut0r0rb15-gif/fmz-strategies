# #431498 RSI双向突破策略RSI-Reversal-Breakout-Strategy -> `fmz_431498_rsi_momentum_reverse`

- FMZ source id: 431498 (lineage).
- Source: https://www.fmz.com/strategy/431498 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-08 12:11:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10000 cash per order stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [12, 24] x `overbought` [70, 60]: **4 trials**; oversold = 100 - overbought.

## Ambiguities resolved

- Default mode only. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
