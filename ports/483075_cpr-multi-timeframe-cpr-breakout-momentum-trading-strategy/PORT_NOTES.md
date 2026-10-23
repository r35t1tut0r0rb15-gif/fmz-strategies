# #483075 多重时间周期CPR突破动量交易策略-Multi-Timeframe-CPR-Breakout-Momentum-Trading-Strategy -> `fmz_483075_daily_cpr_breakout_ema_rsi_divergence_volume_reversal`

- FMZ source id: 483075 (lineage).
- Source: https://www.fmz.com/strategy/483075 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:45:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; previous-day CPR bracket as fractions of the fill |
| 2 | PASS | CPR breakouts with EMA trend, RSI divergence and volume |
| 3 | PASS | No exchange header; no symbol named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_w` [0.5, 1.0] x `tp_w` [1.5, 2.5]: **4 trials**; EMA 20, RSI 14, volume SMA 20.

## Ambiguities resolved

- No header: bar size searched. Negative CPR widths flip the levels, as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "bar_size_pending".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_breakout"`.

## Marks

`bar_size_pending, trailing_stop_pending`
