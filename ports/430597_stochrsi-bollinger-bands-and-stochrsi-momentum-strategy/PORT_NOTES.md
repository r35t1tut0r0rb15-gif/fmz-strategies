# #430597 布林线与StochRSI动量策略Bollinger-Bands-and-StochRSI-Momentum-Strategy -> `fmz_430597_bb_stochrsi_turns`

- FMZ source id: 430597 (lineage).
- Source: https://www.fmz.com/strategy/430597 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-30 17:19:21). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands and a stochastic RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `bb_dev` [2.0, 2.5]: **4 trials**; RSI 14, K / D 3 / 3 fixed.

## Ambiguities resolved

- Stochastic length = K period (3), as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
