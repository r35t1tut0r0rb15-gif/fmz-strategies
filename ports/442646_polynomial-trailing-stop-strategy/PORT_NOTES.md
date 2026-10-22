# #442646 Polynomial Trailing Stop Strategy -> `fmz_442646_sma20_cross_polynomial_rising_stop_long`

- FMZ source id: 442646 (lineage).
- Source: https://www.fmz.com/strategy/442646 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-23 14:43:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit step -> fraction of the stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`degree` [2, 3] x `d_frac` [2.38e-06, 2.38e-05]: **4 trials**; the SMA and low lengths fixed.

## Ambiguities resolved

- Price-unit step as a fraction of the stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
