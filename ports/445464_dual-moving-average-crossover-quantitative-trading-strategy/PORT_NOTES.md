# #445464 Dual Moving Average Crossover Quantitative Trading Strategy -> `fmz_445464_close_sma15_strict_cross_reversal`

- FMZ source id: 445464 (lineage).
- Source: https://www.fmz.com/strategy/445464 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-19 17:16:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [15, 50]: **2 trials**.

## Ambiguities resolved

- Strict crossings. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
