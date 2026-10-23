# #473261 RSI趋势动量交易策略结合双均线和成交量确认-RSI-Trend-Momentum-Trading-Strategy-with-Dual-MA-and-Volume-Confirmation -> `fmz_473261_rsi10_oversold_sma250_500_volume_spike_5pct_stop_long_only`

- FMZ source id: 473261 (lineage).
- Source: https://www.fmz.com/strategy/473261 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:02:32). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 5 % stop from the fill |
| 2 | PASS | Oversold RSI in a long-term uptrend on a volume spike |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_os` [30.0, 25.0] x `sl` [0.05, 0.08]: **4 trials**; RSI 10, SMA 250 / 500, volume x 2.5.

## Ambiguities resolved

- 5 % stop from the fill (source: from the bar after). Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_reversion"`.

## Marks

`coarse_bar_stop`
