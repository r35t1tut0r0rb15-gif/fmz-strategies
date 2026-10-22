# #451071 H1趋势偏差M15-MACD信号M5快速波动率缺口策略-H1-Trend-Bias-M15-MACD-Signal-M5-Fast-Volatility-Gap-Strategy -> `fmz_451071_daily_macd_state_long_bracket_short_churn_reversal`

- FMZ source id: 451071 (lineage).
- Source: https://www.fmz.com/strategy/451071 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-11 17:21:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 15-minute value ends with the daily bar; the long bracket from the fill; the short's wrong-side levels read as a close |
| 2 | PASS | MACD state with a percent bracket on longs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 10 % of equity size and leverage-scaled percents stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.015, 0.03] x `sl` [0.005, 0.01]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- MACD on the day's last 15-minute close; shorts churn on the wrong-side bracket. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
