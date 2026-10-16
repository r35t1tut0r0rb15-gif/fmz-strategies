# #430549 Dual Moving Average Crossover Scalping Strategy -> `fmz_430549_sma_side_confirm_bars`

- FMZ source id: 430549 (lineage).
- Source: https://www.fmz.com/strategy/430549 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 11:19:48). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A moving average and bar colours. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 20, 100] x `confirm_bars` [2, 3]: **6 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
