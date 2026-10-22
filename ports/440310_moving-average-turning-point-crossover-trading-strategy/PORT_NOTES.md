# #440310 Moving Average Turning Point Crossover Trading Strategy -> `fmz_440310_sma25_50_cross_turning_point_exit`

- FMZ source id: 440310 (lineage).
- Source: https://www.fmz.com/strategy/440310 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 11:15:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings and slope turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430020. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [25, 10] x `ma2` [50, 100]: **4 trials**; slope threshold 0.02 % and look-back 1 fixed.

## Ambiguities resolved

- Slope threshold read in roc's percent units. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
