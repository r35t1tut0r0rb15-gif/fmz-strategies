# #434467 Improved Moving Average Crossover Strategy with Market Trend Guidance -> `fmz_434467_double_sma_cross_same_bar`

- FMZ source id: 434467 (lineage).
- Source: https://www.fmz.com/strategy/434467 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-06 16:29:52). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `trend` [50, 100]: **4 trials**; SMA 21 fixed.

## Ambiguities resolved

- Same-bar double crosses, as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
