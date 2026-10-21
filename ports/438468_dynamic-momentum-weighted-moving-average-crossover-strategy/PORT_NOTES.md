# #438468 Dynamic Momentum Weighted Moving Average Crossover Strategy -> `fmz_438468_maema_cross_bb_wick_long`

- FMZ source id: 438468 (lineage).
- Source: https://www.fmz.com/strategy/438468 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 12:04:55). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum-adjusted EMAs and Bollinger bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [80, 40] x `len2` [144, 89]: **4 trials**; MAEMA type, Bollinger 80 and the multipliers fixed.

## Ambiguities resolved

- One position for the two long entries; closes per entry. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
