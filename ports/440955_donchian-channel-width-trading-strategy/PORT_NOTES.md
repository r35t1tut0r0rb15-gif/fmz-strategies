# #440955 Donchian Channel Width Trading Strategy -> `fmz_440955_donchian_width_regime`

- FMZ source id: 440955 (lineage).
- Source: https://www.fmz.com/strategy/440955 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-04 10:35:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C142). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel width against its average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 20] x `smoothe` [50, 20]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_regime"`.

## Marks

`none`
