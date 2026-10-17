# #483118 多重均线趋势追踪与风控优化量化交易策略-Multi-Moving-Average-Trend-Following-and-Risk-Management-Quantitative-Trading-Strategy -> `fmz_483118_ema50_200_rsi_adx_long_atr_trail`

- FMZ source id: 483118 (lineage).
- Source: https://www.fmz.com/strategy/483118 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 14:22:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; the trail a house trail (approximation stated). |
| 2 | PASS | Moving averages, RSI, ADX and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based qty quoted, not ported; the trail via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_k` [1.5, 3.0] x `adx_min` [20.0, 25.0]: **4 trials**; defaults 1.5 / 20 (the source's); EMA 50 / 200, RSI 14
> 50, DMI 14 / 14, the 10-bar confirmation and the 11 % activation fixed.

## Trailing stop (mark `trailing_stop`)

`strategy.exit(trail_points = 1.5 ATR, trail_offset = 1.5 ATR)` on every bar: tick arguments given ATR price
distances, read as price distances (as #427592), become the house trail `{"type": "volatility", "atr_n": 14,
"k": 1.5, "anchor": "high_low", "activate_after": 0.11}`; **stated approximation:** the 1.5-ATR activation becomes an
11 % gain (1.5 daily ATR on DOGE_USDT), as #489284. No fixed stop or target. Promotion of a trailing trial needs the
cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- `barssince` of a condition that never held is na: no entry. Every bar in the condition is an entry signal.
- Long only: opposite entries cannot occur. Stop module: `portfolio_kwargs` {} (D4).
- Broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop, trailing_stop`
