# #439227 基于超级趋势和CCI指标的多时间框架交易策略Best-Supertrend-CCI-Multi-Timeframe-Trading-Strategy -> `fmz_439227_cci_side_of_midline_flip`

- FMZ source id: 439227 (lineage).
- Source: https://www.fmz.com/strategy/439227 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 15:09:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CCI side of a mid line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_period` [28, 14] x `ml` [0.0, 50.0]: **4 trials**.

## Ambiguities resolved

- Long from the first bar while the CCI warms up, as written. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
