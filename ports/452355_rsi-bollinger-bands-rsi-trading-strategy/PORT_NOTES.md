# #452355 布林带RSI交易策略-Bollinger-Bands-RSI-Trading-Strategy -> `fmz_452355_bollinger_rsi_extreme_long`

- FMZ source id: 452355 (lineage).
- Source: https://www.fmz.com/strategy/452355 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-24 17:24:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C187). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band extremes with RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5] x `rsi_len` [14, 7]: **8 trials**; the levels 30 / 70 fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
