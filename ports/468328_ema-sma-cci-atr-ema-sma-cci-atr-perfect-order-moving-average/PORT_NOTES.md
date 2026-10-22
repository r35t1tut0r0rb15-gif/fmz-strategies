# #468328 EMA-SMA-CCI-ATR-均线完美排列策略与趋势魔法指标自动交易系统-EMA-SMA-CCI-ATR-Perfect-Order-Moving-Average-Strategy-with-Trend-Magic-Indicator-Auto-Trading-System -> `fmz_468328_trend_magic_turn_perfect_order_sma90_stop_reversal`

- FMZ source id: 468328 (lineage).
- Source: https://www.fmz.com/strategy/468328 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 15:52:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar levels as fractions of the fill |
| 2 | PASS | CCI sign turns in a perfect MA order with an SMA stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_period` [21, 14] x `rr` [1.5, 3.0]: **4 trials**; the MA lengths fixed.

## Ambiguities resolved

- Marketable signal-bar levels closed one bar late. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
