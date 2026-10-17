# #435132 基于RSI指标的趋势跟踪止损策略Scalping-Strategy-based-on-RSI-Indicator-with-Trailing-Stop-Loss -> `fmz_435132_rsi2_trend_pullback_trail`

- FMZ source id: 435132 (lineage).
- Source: https://www.fmz.com/strategy/435132 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 15:46:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | ADAPT | The tick-sized offset -> a percent of the price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the trail inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.002, 0.01] x `os` [10, 20]: **4 trials**; the overbought level is 100 minus the oversold one; EMA 50 / 200 and RSI 2 fixed.

## Ambiguities resolved

- House percent trail on highs / lows; tick offset -> 0.2 % (the intended 1 % in the grid). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop`
