# #434487 Momentum Breakout Camarilla Support Strategy -> `fmz_434487_weekly_camarilla_fade`

- FMZ source id: 434487 (lineage).
- Source: https://www.fmz.com/strategy/434487 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-06 18:09:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C68). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly levels from completed broker weeks |
| 2 | PASS | Prior-week range levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND428790. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`men_div` [7, 3] x `l_mult` [4.0, 6.0]: **4 trials**; H1 = C + 1.1 R / 12 fixed (`l_mult` sets the L level, 4 = L3).

## Ambiguities resolved

- Last completed broker week's Camarilla levels; empty exits dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
