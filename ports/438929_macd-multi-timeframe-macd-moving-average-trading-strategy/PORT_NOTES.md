# #438929 多时间周期MACD均线交易策略Multi-Timeframe-MACD-Moving-Average-Trading-Strategy -> `fmz_438929_minute_rsi_cross_pin_bar_exit`

- FMZ source id: 438929 (lineage).
- Source: https://www.fmz.com/strategy/438929 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-16 14:06:10). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_sl` [0.029, 1.0] x `rsi_len` [14, 28]: **4 trials**; 65 / 35, pin-bar settings and the 15:1 target fixed.

## Ambiguities resolved

- Minute RSI = the bar's last minute; tick bracket -> ATR multiples. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
