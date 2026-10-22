# #443034 基于ATR和斐波那契回撤止损的趋势跟踪策略ATR-Trailing-Stop-Strategy-with-Fibonacci-Retracement-Targets -> `fmz_443034_two_bar_atr_trail_line_cross_reversal`

- FMZ source id: 443034 (lineage).
- Source: https://www.fmz.com/strategy/443034 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-28 17:09:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close vs ATR trail line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_period` [5, 14] x `atr_factor` [3.5, 2.0]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
