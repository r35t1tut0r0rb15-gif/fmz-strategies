# #432989 Momentum Tracking Strategy -> `fmz_432989_candle_size_trend_follower`

- FMZ source id: 432989 (lineage).
- Source: https://www.fmz.com/strategy/432989 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-23 13:47:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit candle sizes -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`crumb_atr` [5.6, 1.0] x `ema_len` [8, 16]: **4 trials**; timesBigger 2 and the size ratios fixed.

## Ambiguities resolved

- Price-unit candle sizes as ATR multiples (criterion 2 ADAPT). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
