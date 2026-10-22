# #440366 Commodity Channel Index Reversal Trading Strategy -> `fmz_440366_cci_average_cross_reversed`

- FMZ source id: 440366 (lineage).
- Source: https://www.fmz.com/strategy/440366 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-29 16:18:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Averages of the CCI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma` [10, 5] x `reverse` [True, False]: **4 trials**; CCI 10 and slow 20 fixed.

## Ambiguities resolved

- Reverse on by default. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "cci_oscillator"`.

## Marks

`none`
