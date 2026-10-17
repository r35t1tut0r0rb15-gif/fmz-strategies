# #430871 相对强弱指标RSI策略Relative-Strength-Index-RSI-Strategy -> `fmz_430871_rsi_momentum_levels`

- FMZ source id: 430871 (lineage).
- Source: https://www.fmz.com/strategy/430871 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-02 15:54:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [12, 24] x `overbought` [70, 60]: **4 trials**; oversold = 100 - overbought.

## Ambiguities resolved

- Momentum reading as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
