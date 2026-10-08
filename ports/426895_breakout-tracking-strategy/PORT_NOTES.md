# #426895 Breakout Tracking Strategy -> `fmz_426895_donchian_breakout_long`

- Source: https://www.fmz.com/strategy/426895 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-15 12:36:43). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426895` (Jaccard 0.65-0.80) with #442363 (PORT_CANDIDATE); best Jaccard 0.779 with #442363. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 55] x `exit_option` [1, 2]: **4 trials**, defaults 20 / 1 (the source's).

## Ambiguities resolved

- Exit option 1 (lower band) by default; option 2 (basis) in the grid.
- Same bar: from flat the entry stands; while long the close goes flat. Long only.
- FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`none`
