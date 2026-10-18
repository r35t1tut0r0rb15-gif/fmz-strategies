# #435863 Crossing Moving Average Strategy -> `fmz_435863_ema_5_9_21_double_cross`

- FMZ source id: 435863 (lineage).
- Source: https://www.fmz.com/strategy/435863 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-19 13:34:30). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

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

`ema5` [5, 3] x `ema21` [21, 34]: **4 trials**; EMA 9 fixed.

## Ambiguities resolved

- Same-bar double cross as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
