# #473132 MACD-EMA多周期动态交叉量化交易系统-MACD-EMA-Multi-Period-Dynamic-Crossover-Quantitative-Trading-System -> `fmz_473132_macd12_26_9_cross_long_with_emas`

- FMZ source id: 473132 (lineage).
- Source: https://www.fmz.com/strategy/473132 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 14:58:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`setting` [0, 1, 2]: **3 trials** (MACD 12 / 26 / 9, 5 / 35 / 5, 8 / 17 / 9, as #471715).

## Ambiguities resolved

- Same rules as #471715. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
