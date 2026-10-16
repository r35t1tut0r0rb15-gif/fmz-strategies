# #429777 Momentum Dual Moving Average Crossover Strategy -> `fmz_429777_ema_sma50_golden_regime_long`

- FMZ source id: 429777 (lineage).
- Source: https://www.fmz.com/strategy/429777 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-20 16:44:30). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average comparisons only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 25 % of equity, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mom_length` [50, 20] x `bias_slow` [100, 200]: **4 trials**; bias fast 50 fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
