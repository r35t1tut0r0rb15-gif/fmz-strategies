# #442643 基于布林带和MACD的量化交易策略Quantitative-Trading-Strategy-Based-on-Bollinger-Bands-and-MACD -> `fmz_442643_bb200_macd_hist_setups_long`

- FMZ source id: 442643 (lineage).
- Source: https://www.fmz.com/strategy/442643 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 14:30:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit histogram floor -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [200, 100] x `stop_div` [1.01175734321249, 1.02]: **4 trials**; the MACD lengths and the floor fixed.

## Ambiguities resolved

- One id for four setups; floor as a fraction of the close; close-vs-fill stop. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
