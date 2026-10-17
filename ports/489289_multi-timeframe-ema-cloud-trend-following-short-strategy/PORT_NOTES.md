# #489289 多周期指数移动平均云趋势跟踪做空策略-Multi-Timeframe-EMA-Cloud-Trend-Following-Short-Strategy -> `fmz_489289_ema_cloud_cross_down_short_bracket`

- FMZ source id: 489289 (lineage).
- Source: https://www.fmz.com/strategy/489289 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 10:55:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill (deviation stated). |
| 2 | PASS | EMAs and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 2.0] x `tp_pct` [2.0, 4.0]: **4 trials**; defaults 1 / 2 (the source's); EMA 21 / 50 fixed.

## Decision owed: the bracket as written

The exit is issued only on signal bars, from `strategy.position_avg_price`, which is na while flat: a short opened
from flat therefore has no stop or target until a later cross-down re-issues the exit (that entry being ignored). The
port applies the 1 % / 2 % bracket from the fill (the evident intent). Decision owed: keep this, or port the literal
behaviour (no exit until a second cross-down).

## Ambiguities resolved

- The blank resolution is the chart's own timeframe. Short only. FREQ = "2h"; stops on 2-hour bars: `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
