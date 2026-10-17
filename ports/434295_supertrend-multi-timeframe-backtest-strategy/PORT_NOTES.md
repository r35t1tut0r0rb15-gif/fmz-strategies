# #434295 SuperTrend Multi Timeframe Backtest Strategy -> `fmz_434295_supertrend_3_5_side`

- FMZ source id: 434295 (lineage).
- Source: https://www.fmz.com/strategy/434295 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 10:59:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 300 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [3.0, 2.0] x `atr_len` [5, 10]: **4 trials**.

## Ambiguities resolved

- Built-in supertrend rebuilt; the off-by-default square-off dropped. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
