# #365283 MACD ReLoaded -> `fmz_365283_macd_var_reloaded`

- Source: https://www.fmz.com/strategy/365283 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-24 10:15:32). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365283` (Jaccard >= 0.80) with #435290 (DUPLICATE); best Jaccard 0.982 with #435290. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [21, 26] x `trigger` [5, 9] = **8 trials**.

## Ambiguities resolved

- MA type default "VAR" (input() default); nz() seeds kept.
- Date window unused (window() returns true); bar colouring draws.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
