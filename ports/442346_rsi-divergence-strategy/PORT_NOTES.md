# #442346 RSI Divergence Strategy -> `fmz_442346_rsi14_extreme_divergence_reversal`

- FMZ source id: 442346 (lineage).
- Source: https://www.fmz.com/strategy/442346 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 11:43:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price / RSI divergence at extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 9] x `oversold` [30, 20]: **4 trials**; overbought = 100 - oversold.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
