# #440372 Trend Tracking Moving Average Crossover Strategy -> `fmz_440372_vwma66_close_vs_open_2h_long_only`

- FMZ source id: 440372 (lineage).
- Source: https://www.fmz.com/strategy/440372 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 16:52:46). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-weighted close average against the open average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 100, commission 0.1 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars` [66, 35]: **2 trials**; MA type VWMA.

## Ambiguities resolved

- VWMA as written. Volume = broker tick volume (VWMA). Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_weighted_ma"`.

## Marks

`none`
