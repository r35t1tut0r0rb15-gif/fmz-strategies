# #440685 Reversal Breakout Bandpass Combo Strategy -> `fmz_440685_reversal123_bandpass_combo`

- FMZ source id: 440685 (lineage).
- Source: https://www.fmz.com/strategy/440685 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-01 10:45:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C138). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and a bandpass filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_bf` [20, 40]: **4 trials**; delta 0.5, trigger 0 and the 123 smoothing fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
