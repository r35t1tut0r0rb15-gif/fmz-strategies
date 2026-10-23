# #442370 Quantitative Trading Strategy Based on Double Moving Average Crossover -> `fmz_442370_obv_pvt_distance_cross_bar_bracket_1h_long_only`

- FMZ source id: 442370 (lineage).
- Source: https://www.fmz.com/strategy/442370 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 14:28:28). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket at the signal bar as fractions of the fill |
| 2 | PASS | OBV / PVT distance-from-average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 100000, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smoothing` [20, 50] x `limit` [1.0, 3.0]: **4 trials**; stop 1 %, target 5 %.

## Ambiguities resolved

- Distances as written (divide by the line itself). Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "obv"`.

## Marks

`none`
