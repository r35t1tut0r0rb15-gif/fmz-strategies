# #489295 多重蜡烛形态识别与自动交易策略-Multi-Candlestick-Pattern-Recognition-and-Automated-Trading-Strategy -> `fmz_489295_morning_evening_star_bracket`

- FMZ source id: 489295 (lineage).
- Source: https://www.fmz.com/strategy/489295 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:10:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill. |
| 2 | PASS | Candle proportions and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.5, 1.5] x `tp_pct` [1.0, 3.0]: **4 trials**; defaults 0.5 / 1 (the source's); the candle proportions fixed.

## Ambiguities resolved

- `loss` / `profit` (ticks) receive a percentage of the close in price: read as price distances (as #427592).
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop`
