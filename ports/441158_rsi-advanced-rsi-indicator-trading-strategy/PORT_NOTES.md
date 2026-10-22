# #441158 高级RSI指标交易策略Advanced-RSI-Indicator-Trading-Strategy -> `fmz_441158_rsi2_dip_weekly_rsi_filter_daily_exit_long`

- FMZ source id: 441158 (lineage).
- Source: https://www.fmz.com/strategy/441158 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-06 11:47:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C147). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly and daily values from completed periods |
| 2 | PASS | RSI 2 cross, weekly RSI filter and range filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`over_sold` [10, 20] x `weekly_over_sold` [30, 50]: **4 trials**; RSI lengths, exit level and ATR filter fixed.

## Ambiguities resolved

- Weekly / daily values from completed broker weeks / days. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
