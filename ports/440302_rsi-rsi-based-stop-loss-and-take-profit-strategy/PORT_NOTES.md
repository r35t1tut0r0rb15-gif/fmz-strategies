# #440302 基于RSI的止损止盈策略RSI-based-Stop-Loss-and-Take-Profit-Strategy -> `fmz_440302_rsi14_35_65_cross_reversal`

- FMZ source id: 440302 (lineage).
- Source: https://www.fmz.com/strategy/440302 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 10:30:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `oversold` [35, 25]: **4 trials**; overbought = 100 - oversold.

## Ambiguities resolved

- Levels computed but never sent; not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
