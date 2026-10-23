# #458068 EMA-RSI-Volume-Price-Trend-Engulfing-Pattern-均线交叉相对强弱指标成交量价格趋势吞没形态策略 -> `fmz_458068_ema8_20_cross_engulfing_exit_reversal`

- FMZ source id: 458068 (lineage).
- Source: https://www.fmz.com/strategy/458068 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 16:56:08). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA 8 / 20 crossings with engulfing-candle exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [20, 26]: **4 trials**.

## Ambiguities resolved

- The divergence tests can never be true. Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
