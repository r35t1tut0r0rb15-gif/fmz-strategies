# #441052 Dual Moving Average Oscillator Stock Strategy -> `fmz_441052_tsi_signal_cross_long`

- FMZ source id: 441052 (lineage).
- Source: https://www.fmz.com/strategy/441052 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 10:47:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C145). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TSI signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (risk amount unused). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG441052. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_length` [12, 25] x `short_length` [9, 13]: **4 trials**; signal 12 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
