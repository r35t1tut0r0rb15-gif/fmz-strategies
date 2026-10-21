# #436908 Multi indicator Adaptive Trend Trading Strategy -> `fmz_436908_instrument_z_regime_score_long`

- FMZ source id: 436908 (lineage).
- Source: https://www.fmz.com/strategy/436908 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-28 17:59:58). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C98). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target and stops tested on closes |
| 2 | PASS | Score of dimensionless tests; percent exits from the fill price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mat_length` [300, 150] x `ma2_length` [54, 30]: **4 trials**; the second MA length is swept for both regimes together; every other default fixed.

## Ambiguities resolved

- Default switches only; close-tested percent exits from the fill price; VWMA option left out. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
