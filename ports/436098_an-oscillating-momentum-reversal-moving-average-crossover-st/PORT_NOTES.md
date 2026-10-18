# #436098 An Oscillating Momentum Reversal Moving Average Crossover Strategy -> `fmz_436098_macd_histogram_turn_reversal`

- FMZ source id: 436098 (lineage).
- Source: https://www.fmz.com/strategy/436098 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-21 11:21:49). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Histogram turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; signal 9 and the zero levels fixed.

## Ambiguities resolved

- State conditions; year filter dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
