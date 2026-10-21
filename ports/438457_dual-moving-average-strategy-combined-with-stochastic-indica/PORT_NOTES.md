# #438457 Dual Moving Average Strategy Combined with Stochastic Indicator -> `fmz_438457_reversal123_high_low_bands_combo`

- FMZ source id: 438457 (lineage).
- Source: https://www.fmz.com/strategy/438457 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 11:16:52). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and percent bands of a triangular average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `percent_shift` [1.0, 2.0]: **4 trials**; K smoothing 1, D 3, level 50 and HLB length 14 fixed.

## Ambiguities resolved

- 123 test as written; disagreement closes. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
