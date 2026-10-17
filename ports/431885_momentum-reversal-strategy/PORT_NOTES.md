# #431885 Momentum Reversal Strategy -> `fmz_431885_five_bar_change_momentum`

- FMZ source id: 431885 (lineage).
- Source: https://www.fmz.com/strategy/431885 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 10:02:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A percentage change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`x` [5, 10] x `pct` [0.4, 1.0]: **4 trials**; the short threshold = -pct.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
