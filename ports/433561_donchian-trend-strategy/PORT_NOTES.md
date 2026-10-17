# #433561 Donchian Trend Strategy -> `fmz_433561_donchian_position_trend`

- FMZ source id: 433561 (lineage).
- Source: https://www.fmz.com/strategy/433561 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-28 15:13:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Crosses of a channel-position line with its average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [42, 20] x `slow` [45, 90]: **4 trials**; fast EMA 5 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
