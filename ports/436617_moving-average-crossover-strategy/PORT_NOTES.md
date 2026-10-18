# #436617 Moving Average Crossover Strategy -> `fmz_436617_sma_cross_reversal_daily`

- FMZ source id: 436617 (lineage).
- Source: https://www.fmz.com/strategy/436617 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-26 12:04:34). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C93). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 20] x `long_len` [40, 80]: **4 trials**.

## Ambiguities resolved

- EMA 20 only drawn. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
