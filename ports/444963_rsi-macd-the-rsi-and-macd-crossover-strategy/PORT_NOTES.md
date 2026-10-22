# #444963 基于RSI和MACD交叉策略The-RSI-and-MACD-Crossover-Strategy -> `fmz_444963_macd_hist_zero_rsi_side_cross_reversal`

- FMZ source id: 444963 (lineage).
- Source: https://www.fmz.com/strategy/444963 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 15:08:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram and RSI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `oversold` [40, 30]: **4 trials**; the overbought level and the MACD lengths fixed.

## Ambiguities resolved

- No exit (blocks commented out). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
