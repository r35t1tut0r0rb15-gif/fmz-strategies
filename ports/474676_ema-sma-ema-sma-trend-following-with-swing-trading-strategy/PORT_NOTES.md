# #474676 EMA-SMA趋势跟踪与波段交易策略结合成交量过滤和百分比止盈止损系统-EMA-SMA-Trend-Following-with-Swing-Trading-Strategy-Combined-Volume-Filter-and-Percentage-Take-Profit-Stop-Loss-System -> `fmz_474676_swing_pivot_breakout_volume200_2pct_target_reversal`

- FMZ source id: 474676 (lineage).
- Source: https://www.fmz.com/strategy/474676 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 15:12:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 2 % target from the fill |
| 2 | PASS | Swing-level breakouts on high volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot` [6, 10] x `tp` [0.02, 0.04]: **4 trials**; volume SMA 200.

## Ambiguities resolved

- No trailing stop (no activation level); 2 % target from the fill. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "swing_breakout"`.

## Marks

`coarse_bar_stop`
