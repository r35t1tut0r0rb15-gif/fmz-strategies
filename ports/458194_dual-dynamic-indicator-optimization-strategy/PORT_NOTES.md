# #458194 Dual Dynamic Indicator Optimization Strategy -> `fmz_458194_close_sma14_cross_reversal`

- FMZ source id: 458194 (lineage).
- Source: https://www.fmz.com/strategy/458194 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 17:03:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

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

`ma_len` [14, 50]: **2 trials**; the switches at their defaults.

## Ambiguities resolved

- Default switches only (strategy 2 off). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
