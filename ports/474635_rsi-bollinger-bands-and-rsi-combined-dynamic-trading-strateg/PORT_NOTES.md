# #474635 布林带与RSI指标组合动态交易策略-Bollinger-Bands-and-RSI-Combined-Dynamic-Trading-Strategy -> `fmz_474635_bb20_reentry_rsi30_70_long`

- FMZ source id: 474635 (lineage).
- Source: https://www.fmz.com/strategy/474635 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 11:21:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band re-entries at RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**; the RSI levels fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
