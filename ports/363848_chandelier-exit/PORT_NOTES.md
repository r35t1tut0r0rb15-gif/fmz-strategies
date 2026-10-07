# #363848 Chandelier Exit -> `fmz_363848_chandelier_exit_flip`

- Source: https://www.fmz.com/strategy/363848 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-17 17:14:58). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

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

`length` [14, 22, 34] x `mult` [2.0, 3.0, 4.0] = **9 trials**.

## Ambiguities resolved

- "Use Close Price for Extremums" default true: highest/lowest of close.
- `dir` is a var starting at 1.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`none`
