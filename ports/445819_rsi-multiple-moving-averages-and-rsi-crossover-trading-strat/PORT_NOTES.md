# #445819 多重均线与RSI交叉交易策略Multiple-Moving-Averages-and-RSI-Crossover-Trading-Strategy -> `fmz_445819_macd_cross_ema9_21_order_rsi_reversal`

- FMZ source id: 445819 (lineage).
- Source: https://www.fmz.com/strategy/445819 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-22 14:38:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings with EMA order and RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 34]: **4 trials**; the RSI and MACD settings fixed.

## Ambiguities resolved

- Closes after reversing entries leave them. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
