# #483027 动态趋势RSI交叉动量增强策略-Dynamic-Trend-RSI-Crossover-Momentum-Enhancement-Strategy -> `fmz_483027_sma10_atr3_flip_line_side_rsi14_state_reversal`

- FMZ source id: 483027 (lineage).
- Source: https://www.fmz.com/strategy/483027 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 10:00:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band-line side with RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_length` [10, 20] x `factor` [3.0, 2.0]: **4 trials**; RSI 14 / 30 / 70.

## Ambiguities resolved

- The hand-built line is kept as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
