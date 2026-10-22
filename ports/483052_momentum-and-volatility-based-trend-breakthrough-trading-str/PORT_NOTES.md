# #483052 Momentum and Volatility Based Trend Breakthrough Trading Strategy -> `fmz_483052_pctb_0_2_0_8_cmo14_zero_cross_reversal`

- FMZ source id: 483052 (lineage).
- Source: https://www.fmz.com/strategy/483052 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:09:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | %B and CMO crossings together |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 40] x `cmo_length` [14, 9]: **4 trials**; band 2 sd, %B levels 0.2 / 0.8.

## Ambiguities resolved

- REVERSAL INTENDED, no other exit. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
