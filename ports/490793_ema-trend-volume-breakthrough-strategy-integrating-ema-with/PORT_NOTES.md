# #490793 趋势量能突破策略整合EMA与成交量异常监测系统-Trend-Volume-Breakthrough-Strategy-Integrating-EMA-with-Volume-Anomaly-Detection-System -> `fmz_490793_volume_spike_candle_ema50_5bar_exit_4d_reversal`

- FMZ source id: 490793 (lineage).
- Source: https://www.fmz.com/strategy/490793 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-16 15:16:18). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a bar-count exit in the signals |
| 2 | PASS | Volume-spike candles in the EMA 50 trend with a time exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`exit_bars` [5, 3] x `vol_mult` [2.0, 1.5]: **4 trials**; volume EMA 20, EMA 50.

## Ambiguities resolved

- Counter restarts on repeated signals. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "4D" (4-broker-day blocks).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_breakout"`.

## Marks

`none`
