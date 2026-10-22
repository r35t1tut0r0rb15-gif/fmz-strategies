# #440094 Multiple Indicators Follow Strategy -> `fmz_440094_reversal123_qstick_combo`

- FMZ source id: 440094 (lineage).
- Source: https://www.fmz.com/strategy/440094 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 15:42:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and candle-body average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_q` [14, 30]: **4 trials**; the 123 smoothing fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
