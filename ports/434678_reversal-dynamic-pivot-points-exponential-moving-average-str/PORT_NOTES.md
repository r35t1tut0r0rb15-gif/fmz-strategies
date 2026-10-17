# #434678 Reversal Dynamic Pivot Points Exponential Moving Average Strategy -> `fmz_434678_combo_123_daily_pivot`

- FMZ source id: 434678 (lineage).
- Source: https://www.fmz.com/strategy/434678 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-08 11:37:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | Oscillator levels and prior-day pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG434678, ND431662. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `level` [50, 30]: **4 trials**; the 123 smoothing / D length fixed.

## Ambiguities resolved

- Last completed broker day's pivots. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
