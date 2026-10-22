# #442947 Combo Quantitative Trend Tracking Strategy -> `fmz_442947_reversal123_rainbow_oscillator_combo`

- FMZ source id: 442947 (lineage).
- Source: https://www.fmz.com/strategy/442947 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-27 15:54:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and rainbow states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_ro` [2, 4]: **4 trials**; the HHV / LLV lookback fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
