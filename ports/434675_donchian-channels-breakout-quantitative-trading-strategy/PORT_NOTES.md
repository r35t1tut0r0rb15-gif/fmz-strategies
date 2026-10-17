# #434675 Donchian Channels Breakout Quantitative Trading Strategy -> `fmz_434675_donchian50_breakout_long`

- FMZ source id: 434675 (lineage).
- Source: https://www.fmz.com/strategy/434675 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-08 11:00:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | Channel breakouts and a percent stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The money-per-trade quantity and the monetary stop stored (the stop re-expressed as 10 %). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [50, 20] x `sl_pct` [0.10, 0.05]: **4 trials**; the exit channel is period // 4.

## Ambiguities resolved

- Monetary stop -> 10 % of the fill; year filter dropped. Flat tracked through the stop and the exit. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop`
