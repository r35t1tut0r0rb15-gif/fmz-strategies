# #478685 动态神经网络RSI趋势跟踪交易策略-Dynamic-Neural-RSI-Trend-Following-Trading-Strategy -> `fmz_478685_sma200_up_rsi40_dip_close_ratchet_cooldown_long`

- FMZ source id: 478685 (lineage).
- Source: https://www.fmz.com/strategy/478685 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 14:19:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C238). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI dips in an SMA 200 up-trend with a close ratchet and a cool-down |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [5.0, 2.0] x `waiting_days` [10, 2]: **4 trials**; SMA 200, RSI 14 / 40.

## Ambiguities resolved

- Long only. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
