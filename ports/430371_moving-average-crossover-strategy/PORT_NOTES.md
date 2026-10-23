# #430371 Moving Average Crossover Strategy -> `fmz_430371_dynamic_ema5_sma10_trend13_cross_reversal`

- FMZ source id: 430371 (lineage).
- Source: https://www.fmz.com/strategy/430371 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-27 16:19:00). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Dynamic EMA / SMA crossings in an ordered trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity, capital 100000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema1` [5, 9] x `sma1` [10, 20]: **4 trials**; trend SMA 13.

## Ambiguities resolved

- Filters off (no volume). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_crossover"`.

## Marks

`none`
