# #442397 基于均线和EMA的跨时间框架趋势策略Multi-Timeframe-Moving-Average-and-EMA-Based-Trend-Strategy -> `fmz_442397_sma_pullback_bar_and_profit_count_exit_long`

- FMZ source id: 442397 (lineage).
- Source: https://www.fmz.com/strategy/442397 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-21 15:59:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C155). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA pullback entry with bar / profit counters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_profit_closes` [5, 3] x `max_bars` [10, 20]: **4 trials**; the MA lengths fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
