# #436238 Single Moving Average Crossover Bollinger Bands Strategy -> `fmz_436238_sma_deviation_band_cross`

- FMZ source id: 436238 (lineage).
- Source: https://www.fmz.com/strategy/436238 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-22 14:10:14). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Exit orders without arguments: none |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the off bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`s` [90, 60] x `p` [0.9, 1.5]: **4 trials**.

## Ambiguities resolved

- Exit orders without arguments do nothing. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
