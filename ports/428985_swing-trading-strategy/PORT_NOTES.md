# #428985 Swing Trading Strategy -> `fmz_428985_ema20_50_trend_bracket`

- FMZ source id: 428985 (lineage).
- Source: https://www.fmz.com/strategy/428985 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-11 16:29:37). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Moving-average crosses and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy(), leverage and quantity stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428985. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 2.0] x `tp_pct` [1.0, 2.0]: **4 trials**; EMAs 20 / 50 / 200 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. Mark coarse_bar_stop. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
