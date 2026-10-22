# #441042 Reversal Trend Catching and Dynamic Stop Loss Combo Strategy -> `fmz_441042_reversal123_kase_dev_stops_combo`

- FMZ source id: 441042 (lineage).
- Source: https://www.fmz.com/strategy/441042 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 09:54:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and Kase levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_kds` [30, 20]: **4 trials**; level 4 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
