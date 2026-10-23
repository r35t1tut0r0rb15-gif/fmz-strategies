# #477551 双周期移动平均线结合RSI动量和成交量的趋势跟踪策略-Dual-Period-Moving-Average-with-RSI-Momentum-and-Volume-Trend-Following-Strategy -> `fmz_477551_sma21_rsi_avg_volume_state_sma55_exit_long_only`

- FMZ source id: 477551 (lineage).
- Source: https://www.fmz.com/strategy/477551 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 13:45:16). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend-and-momentum state entries on volume with MA / RSI crossing exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 13] x `slow` [55, 89]: **4 trials**; RSI 13 / 13, volume SMA 21.

## Ambiguities resolved

- Entry kept over a same-bar close from flat. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_momentum"`.

## Marks

`none`
