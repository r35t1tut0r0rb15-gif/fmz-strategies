# #432920 Modern Laguerre Transform Relative Strength Index Optimization Strategy -> `fmz_432920_laguerre_rsi_zones`

- FMZ source id: 432920 (lineage).
- Source: https://www.fmz.com/strategy/432920 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-22 17:38:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A bounded oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gamma` [0.5, 0.7] x `band` [0.8, 0.7]: **4 trials**; the sell band is 1 - band (0.2 as written).

## Ambiguities resolved

- Filter states seeded with 1 as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
