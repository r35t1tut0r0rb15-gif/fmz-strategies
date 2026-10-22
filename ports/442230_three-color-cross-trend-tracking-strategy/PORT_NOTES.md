# #442230 Three Color Cross Trend Tracking Strategy -> `fmz_442230_three_line_strike_pullback_reversal`

- FMZ source id: 442230 (lineage).
- Source: https://www.fmz.com/strategy/442230 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 14:19:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle sequence |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`run` [3, 2]: **2 trials** (candles in the run).

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
