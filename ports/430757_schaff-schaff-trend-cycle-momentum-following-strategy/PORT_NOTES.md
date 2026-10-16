# #430757 动量跟随的Schaff趋势循环策略Schaff-Trend-Cycle-Momentum-Following-Strategy -> `fmz_430757_schaff_trend_cycle`

- FMZ source id: 430757 (lineage).
- Source: https://www.fmz.com/strategy/430757 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-01 16:08:35). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A bounded cycle oscillator. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG430757. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [23, 12] x `cycle_length` [10, 20]: **4 trials**; slow 50, %D 3 / 3 and levels 75 / 25 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
