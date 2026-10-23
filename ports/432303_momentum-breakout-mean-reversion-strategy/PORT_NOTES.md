# #432303 Momentum Breakout Mean Reversion Strategy -> `fmz_432303_ema3_pullback_volume_drop_time_profit_count_exit_long`

- FMZ source id: 432303 (lineage).
- Source: https://www.fmz.com/strategy/432303 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-16 10:47:41). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pullback entries with time and profit-count exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = 1 unit, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_bars` [10, 20] x `max_profit_closes` [5, 3]: **4 trials**; EMA 3.

## Ambiguities resolved

- Counters as written (fill bar = bar 1). Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pullback_time_exit"`.

## Marks

`none`
