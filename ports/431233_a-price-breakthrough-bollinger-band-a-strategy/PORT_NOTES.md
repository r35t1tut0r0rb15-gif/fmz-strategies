# #431233 价格突破布林线A策略Price-Breakthrough-Bollinger-Band-A-Strategy -> `fmz_431233_bb_stoch_rsi_reentry`

- FMZ source id: 431233 (lineage).
- Source: https://www.fmz.com/strategy/431233 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-06 11:43:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger bands, stochastic RSI and an EMA slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `mult` [1.5, 2.0]: **4 trials**; stoch RSI 11 / 7 / 3 / 4, level 20 and EMA 7 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
