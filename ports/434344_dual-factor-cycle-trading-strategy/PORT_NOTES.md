# #434344 Dual factor Cycle Trading Strategy -> `fmz_434344_combo_123_cosrl_weekly`

- FMZ source id: 434344 (lineage).
- Source: https://www.fmz.com/strategy/434344 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 17:56:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed broker weeks |
| 2 | PASS | Oscillator levels and prior-week levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `to_line` [True, False]: **4 trials**; the 123 smoothing / D length / level fixed.

## Ambiguities resolved

- Last completed broker week's high / low. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
