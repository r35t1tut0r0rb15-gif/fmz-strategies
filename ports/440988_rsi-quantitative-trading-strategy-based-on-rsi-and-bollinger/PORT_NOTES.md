# #440988 基于RSI和布林带的量化交易策略Quantitative-Trading-Strategy-Based-on-RSI-and-Bollinger-Bands -> `fmz_440988_rsi_bb_joint_reentry_reversal`

- FMZ source id: 440988 (lineage).
- Source: https://www.fmz.com/strategy/440988 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 15:22:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI and Bollinger crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `oversold` [30, 40]: **4 trials**; overbought = 100 - oversold.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
