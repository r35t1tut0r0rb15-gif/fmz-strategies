# #439870 Moving Average Crossover Trading Strategy -> `fmz_439870_ema4_8_side_ema20_slope_state`

- FMZ source id: 439870 (lineage).
- Source: https://www.fmz.com/strategy/439870 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-24 14:59:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA side and slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`e2` [8, 13] x `e3` [20, 50]: **4 trials**; EMA 4 fixed.

## Ambiguities resolved

- Level-free exits place nothing. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
