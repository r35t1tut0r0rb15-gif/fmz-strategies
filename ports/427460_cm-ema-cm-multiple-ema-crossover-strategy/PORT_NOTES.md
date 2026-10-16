# #427460 CM Multiple EMA Crossover Strategy -> `fmz_427460_cm_ema_trend_cross`

- FMZ source id: 427460 (lineage).
- Source: https://www.fmz.com/strategy/427460 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 12:12:56). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mid` [21, 13] x `slow` [55, 89] x `filt` [13, 8]: **8 trials**; defaults 21 / 55 / 13 (the source's). EMA 8 only appears as a boolean (always true).

## Ambiguities resolved

- The `strategy.close` calls name ids no entry uses: they never act. The opposite cross is the only exit (REVERSAL INTENDED).
- FREQ = "6h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
