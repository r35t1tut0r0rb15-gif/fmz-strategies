# #482899 动态突破追踪止损交易策略基于波动率的多周期价格突破模型-Dynamic-Breakout-Trading-Strategy-with-Multi-Period-Volatility-Based-Price-Breakthrough-Model -> `fmz_482899_breakout_pct_trail_2d`

- FMZ source id: 482899 (lineage).
- Source: https://www.fmz.com/strategy/482899 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:27:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; the trail a house trail. |
| 2 | PASS | Rolling extremes and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the pyramiding adds quoted, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.2, 1.0] x `lookback` [10, 20]: **4 trials**; defaults 0.2 / 10 (the source's); the 0.05 % threshold
and the 0.5 % activation fixed.

## Trailing stop (mark `trailing_stop`)

`trail_points = close x 0.5 %`, `trail_offset = close x 0.2 %`: tick arguments given price distances, read as price
distances (as #427592), become `{"type": "percent", "pct": 0.002, "anchor": "high_low", "activate_after": 0.005}`.
Promotion of a trailing trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- pyramiding = 100 adds on each breakout: adds are sizing, not ported (as #490570). The 1-hour spacing always holds on
  two-day bars.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Two-day blocks of broker-day dates (decision owed, as
  #426509); FREQ = "2D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop, trailing_stop`
