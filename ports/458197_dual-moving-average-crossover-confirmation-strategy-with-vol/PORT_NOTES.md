# #458197 Dual Moving Average Crossover Confirmation Strategy with Volume Price Integration Optimization Model -> `fmz_458197_close_cross_sma20_and_sma50_same_bar_reversal`

- FMZ source id: 458197 (lineage).
- Source: https://www.fmz.com/strategy/458197 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 17:12:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Double SMA crossings on one bar |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [20, 10] x `long_len` [50, 100]: **4 trials**.

## Ambiguities resolved

- Signals traded, confirmations unused (as written). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
