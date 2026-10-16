# #430125 Trend Following Dual Moving Average Strategy -> `fmz_430125_adxr_levels`

- FMZ source id: 430125 (lineage).
- Source: https://www.fmz.com/strategy/430125 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-25 11:42:23). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ADX levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_adx` [14, 28] x `signal1` [13, 20]: **4 trials**; ADXR lag = ADX length; signal 2 45 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
