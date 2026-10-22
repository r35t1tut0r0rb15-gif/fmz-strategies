# #488283 多时段价格行为机构交易策略基于ICT理念的日内做空系统-Multi-Session-Price-Action-Institutional-Trading-Strategy-ICT-Based-Intraday-Short-System -> `fmz_488283_london_range_judas_short_london_low_buy_tick_bracket`

- FMZ source id: 488283 (lineage).
- Source: https://www.fmz.com/strategy/488283 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 15:40:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C266). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; tick brackets as fractions of the fill |
| 2 | ADAPT | Tick brackets read as percents at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_ticks` [10, 30] x `tp_ticks` [20, 60]: **4 trials**; ticks at 0.01 / 3000 of the price.

## Ambiguities resolved

- The never-reset London range depends on the data start, as written; the Asia short never trades. Ticks read at ETH 3000. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "session_breakout"`.

## Marks

`trailing_stop_pending`
