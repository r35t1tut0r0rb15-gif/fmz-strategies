# #489189 TrendSync-Pro-SMC-多时间框架趋势跟随策略-TrendSync-Pro-SMC-Multi-Timeframe-Trend-Following-Strategy -> `fmz_489189_pivot20_level_cross_pct_bracket_level_exit_flat`

- FMZ source id: 489189 (lineage).
- Source: https://www.fmz.com/strategy/489189 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 15:42:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C270). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | Pivot-level crossings with a percent bracket and level exits |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 1 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trend_period` [20, 10] x `sl_percent` [1.0, 2.0]: **4 trials** (target 2 x the stop).

## Ambiguities resolved

- Entries only from flat (a loop follows the bracket and level exits). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_breakout"`.

## Marks

`none`
