# #440096 Adaptive Linear Regression Channel Strategy -> `fmz_440096_stealthy7_regression_channel_open`

- FMZ source id: 440096 (lineage).
- Source: https://www.fmz.com/strategy/440096 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-26 15:48:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression channel of past closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `mult` [1.0, 2.0]: **4 trials**; the same multiplier on both sides.

## Ambiguities resolved

- Final close_all leaves the bar flat. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
