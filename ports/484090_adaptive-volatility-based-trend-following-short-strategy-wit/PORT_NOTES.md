# #484090 时间延迟与止损保护的自适应波动率趋势跟踪空头策略-Adaptive-Volatility-Based-Trend-Following-Short-Strategy-with-Time-Delay-and-Stop-Loss-Protection -> `fmz_484090_short_sma_breakdown_delayed_exit`

- FMZ source id: 484090 (lineage).
- Source: https://www.fmz.com/strategy/484090 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 09:42:59). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and bar-range-checked exits. |
| 2 | PASS | Moving averages, ATR and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [0.5, 1.0] x `delay_min` [10, 30]: **4 trials**; defaults 0.5 / 10 (the source's); SMA 50 / 200, ATR 14 vs
its 28-bar average and the 20-bar 0.03 % range test fixed.

## Ambiguities resolved

- As written the exit tests run only inside the outer condition block; outside it the trade is held. The 0.5 % stop
  is bar-range-checked with `strategy.close`: an exit signal at the next open (#489638). The script's flag gates the
  entries; closes act on the position at the bar's start (#430850), so a close on the entry's own bar does not undo
  the entry. The delay counts bar open times. Short only: opposite entries cannot occur. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_filter"`.

## Marks

`none`
