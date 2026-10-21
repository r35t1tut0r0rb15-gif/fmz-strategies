# #438451 Moving Average Crossover Trend Strategy -> `fmz_438451_day_open_sma60_275_bracket_long`

- FMZ source id: 438451 (lineage).
- Source: https://www.fmz.com/strategy/438451 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 10:56:57). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; daily value from completed days |
| 2 | PASS | Moving-average crossings of the day open; percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [60, 30] x `slow` [275, 150]: **4 trials**; the 13 % / 42 % bracket fixed.

## Ambiguities resolved

- Previous day's open from completed days; bracket fixed at the fill. Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
