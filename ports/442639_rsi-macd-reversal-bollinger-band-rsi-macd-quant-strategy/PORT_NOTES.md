# #442639 反转布林带RSI-MACD量化策略Reversal-Bollinger-Band-RSI-MACD-Quant-Strategy -> `fmz_442639_bb_rsi_macd_extreme_reversal`

- FMZ source id: 442639 (lineage).
- Source: https://www.fmz.com/strategy/442639 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-23 14:16:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band, RSI and MACD extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_bb` [20, 50] x `oversold` [30, 20]: **4 trials** (overbought = 100 - oversold); the MACD lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
