# #427809 Dual Thrust Indicator Strategy -> `fmz_427809_daily_pivot_cross_supertrend_exit`

- FMZ source id: 427809 (lineage).
- Source: https://www.fmz.com/strategy/427809 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-25 17:34:46). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | `security("D", x[1], lookahead_on)` = previous completed day; bar-close orders. |
| 2 | PASS | Pivots from prices, ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [2, 3] x `pd` [10, 20] x `ma` [20, 50]: **8 trials**; defaults 2 / 10 / 20 (the source's); pivot type Daily fixed.

## Ambiguities resolved

- Broker days built from the 2-hour bars by start time (summer straddle stated). Intraday / weekly pivot options not ported; R / S levels drawn only.
- Closes are exit signals; REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
