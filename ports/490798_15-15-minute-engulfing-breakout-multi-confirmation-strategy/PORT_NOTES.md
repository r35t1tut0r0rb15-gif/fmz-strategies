# #490798 15分钟图表吞没突破多重确认策略-15-Minute-Engulfing-Breakout-Multi-Confirmation-Strategy -> `fmz_490798_engulfing_zone_retest_bracket`

- FMZ source id: 490798 (lineage).
- Source: https://www.fmz.com/strategy/490798 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-16 15:33:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; zone bracket from the signal bar (re-placement marked). |
| 2 | PASS | Candle and zone levels; the inert 0.003 price-unit offset dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`memory` [10, 5] x `breaks` [2, 3]: **4 trials**; defaults 10 / 2 (the source's).

## Re-placed bracket (rule 2, mark `trailing_stop_pending`)

The bracket (stop at the zone low, target at the zone high) is issued with each entry signal under the shared id
"TP/SL"; a new zone retest while the trade is open re-places it at the new zone. The port keeps the bracket of the
entry (`sl_stop` / `tp_stop` from the signal bar, re-based on the fill).

## Ambiguities resolved

- A signal whose close is already beyond its target (only the low must reach the zone) would exit at once on the
  fill in the source; no entry is emitted for it, and the zone is still cleared.
- The 30-pip offset (0.003 in price) is inert on BTC_USDT: dropped.
- Both signals on one bar: the short (written last) wins. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
