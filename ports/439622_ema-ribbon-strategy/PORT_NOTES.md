# #439622 EMA Ribbon Strategy -> `fmz_439622_ema_ribbon_20_55_cross`

- FMZ source id: 439622 (lineage).
- Source: https://www.fmz.com/strategy/439622 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-22 12:21:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length1` [20, 10] x `length8` [55, 100]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
