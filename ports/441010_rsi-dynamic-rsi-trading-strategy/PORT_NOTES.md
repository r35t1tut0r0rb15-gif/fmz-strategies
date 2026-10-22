# #441010 动态RSI指标交易策略Dynamic-RSI-Trading-Strategy -> `fmz_441010_rsi_30_70_cross_close_level_exits`

- FMZ source id: 441010 (lineage).
- Source: https://www.fmz.com/strategy/441010 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 17:36:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit change test -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 9] x `trail_pct` [3, 5]: **4 trials**; levels and the change fraction fixed.

## Ambiguities resolved

- Close-built level and price-unit change test as written (change as a fraction at BTC 42000). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
