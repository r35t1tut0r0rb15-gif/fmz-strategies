# #430276 双EMA黄绿交易系统Trend-Trading-with-Double-EMA-Crossover-System -> `fmz_430276_vins_playzone`

- FMZ source id: 430276 (lineage).
- Source: https://www.fmz.com/strategy/430276 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-26 17:15:46). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages and a stochastic RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [12, 8] x `ema_slow` [26, 50]: **4 trials**; smoothing 2 and the stochastic RSI settings fixed.

## Ambiguities resolved

- Same-timeframe security = the chart's EMAs. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
