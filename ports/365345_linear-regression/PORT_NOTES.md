# #365345 Linear Regression ++ [Lucem Anb] -> `fmz_365345_linreg_channel_reversion`

- Source: https://www.fmz.com/strategy/365345 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-24 14:17:42). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A12). Not run.

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

`length` [50, 100, 200] x `dev` [1.5, 2.0, 2.5] = **9 trials**.

## Ambiguities resolved

- Resolution "" = chart; smoothing 1 = the series itself.
- Channel from the series' own regression residuals over the window (no whole-series statistic).
- `FREQ = "45min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks (2026-10-07)

`none`
