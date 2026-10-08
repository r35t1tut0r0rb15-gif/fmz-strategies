# #426521 Fast and Slow EMA Crossover Trend Trading Strategy -> `fmz_426521_ema_13_48_long`

- Source: https://www.fmz.com/strategy/426521 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-12 18:06:26). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG426521` (Jaccard >= 0.80) with #430973 (DUPLICATE); best Jaccard 1.000 with #430973. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 13, 21] x `slow` [48, 100]: **6 trials**, defaults 13 / 48 (the source's).

## Ambiguities resolved

- Long only (short orders commented out).
- Daily bars are broker days.

- Same bar: from flat an entry stands; while long the close goes flat (Pine order).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
