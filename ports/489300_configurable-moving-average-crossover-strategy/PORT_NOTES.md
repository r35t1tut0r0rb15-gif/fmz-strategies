# #489300 Configurable Moving Average Crossover Strategy -> `fmz_489300_close_ema13_cross_ema55_stack_ema34_exit_long`

- FMZ source id: 489300 (lineage).
- Source: https://www.fmz.com/strategy/489300 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:31:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA breakouts in an EMA stack with an EMA exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`maPeriodA` [13, 8] x `maPeriodC` [34, 21]: **4 trials**; EMA 55.

## Ambiguities resolved

- Long only. FREQ = "2D" (two broker days). MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
