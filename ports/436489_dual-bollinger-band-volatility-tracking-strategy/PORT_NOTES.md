# #436489 Dual Bollinger Band Volatility Tracking Strategy -> `fmz_436489_bollinger_either_band_cross`

- FMZ source id: 436489 (lineage).
- Source: https://www.fmz.com/strategy/436489 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-25 11:49:41). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C89). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- Either band crossing trades. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
