# #364536 HODL LINE -> `fmz_364536_hodl_line_cross`

- Source: https://www.fmz.com/strategy/364536 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-20 16:59:54). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [50, 100, 300, 500] (the four sensitivity options) x `hma_len` [25, 50] = **8 trials**. Asymmetry 0.05 stays at the original.

## Ambiguities resolved

- Sensitivity default "Hold Short Term" = length 100.
- `ta.hma` with `round(sqrt(n))`; the line is a price ratio (scale-free).
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`none`
