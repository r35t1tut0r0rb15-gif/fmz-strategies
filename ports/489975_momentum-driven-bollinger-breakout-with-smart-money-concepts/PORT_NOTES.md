# #489975 动量驱动型布林带突破与智能资金概念融合策略-Momentum-Driven-Bollinger-Breakout-with-Smart-Money-Concepts-Integration-Strategy -> `fmz_489975_bb55_breakout_structure_momentum`

- FMZ source id: 489975 (lineage).
- Source: https://www.fmz.com/strategy/489975 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-10 16:12:38). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bands, swing levels and candle proportions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 5 %-of-equity quantity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [55, 20] x `body_pct` [0.7, 0.5]: **4 trials**; defaults 55 / 0.7 (the source's); multiplier 2 and swing
12 fixed.

## Ambiguities resolved

- The '1D' security on the daily chart is the bar's own close; the trend filter is close vs the basis.
- The order-block exits (close beyond the 20-bar extreme including the current bar, x 0.99 / 1.01) can never fire:
  inert, left out.
- Closes act on the position held at the bar's start. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
