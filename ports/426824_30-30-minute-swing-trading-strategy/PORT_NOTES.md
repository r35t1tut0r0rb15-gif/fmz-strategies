# #426824 30 Minute Swing Trading Strategy -> `fmz_426824_hull_slope`

- Source: https://www.fmz.com/strategy/426824 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 17:44:03). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [35, 70, 100]: **3 trials**, default 70 (the source's).

## Ambiguities resolved

- Warm-up: `n2 >= n1` with na is false, so the source is long (as Pine).
- RSI / EMA / stop inputs feed unused variables.
- FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "slope_momentum"`.

## Marks (2026-10-07)

`none`
