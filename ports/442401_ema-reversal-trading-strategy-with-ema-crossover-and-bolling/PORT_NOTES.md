# #442401 双EMA穿越与布林带回转策略Reversal-Trading-Strategy-with-EMA-Crossover-and-Bollinger-Bands -> `fmz_442401_ema50_200_cross_band_break_reversal`

- FMZ source id: 442401 (lineage).
- Source: https://www.fmz.com/strategy/442401 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 16:12:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C155). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings and band breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_short` [50, 20] x `bb_length` [20, 50]: **4 trials**; EMA 200 and the multiplier fixed.

## Ambiguities resolved

- Same-bar Buy and Sell: Sell wins. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
