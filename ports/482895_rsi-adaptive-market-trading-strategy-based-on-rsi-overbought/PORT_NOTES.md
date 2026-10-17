# #482895 基于RSI超买超卖的自适应市场交易策略-Adaptive-Market-Trading-Strategy-Based-on-RSI-Overbought-Oversold -> `fmz_482895_rsi_extremes_utc_window_pct_bracket`

- FMZ source id: 482895 (lineage).
- Source: https://www.fmz.com/strategy/482895 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:28:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | RSI and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 0.5] x `tp_pct` [2.0, 1.0]: **4 trials**; defaults 1 / 2 (the source's); RSI 14 (70 / 30) and the
06:00-17:00 UTC window fixed.

## Trailing stop (mark `trailing_stop_pending`)

Every bar in the RSI zone re-places the stop and target from the new close while held. The port keeps the entry's
bracket.

## Ambiguities resolved

- Clock (C6): `hour(time)` in UTC (the author's Binance chart), entries 06:00-16:59 UTC. "Gold" is a label.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`trailing_stop_pending`
