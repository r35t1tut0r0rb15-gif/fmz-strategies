# #363825 Supertrend+4moving -> `fmz_363825_close_supertrend_flip`

- Source: https://www.fmz.com/strategy/363825 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-17 15:35:18). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A10). Not run.

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

`period` [10, 20, 30] x `mult` [2.0, 3.0, 4.0] = **9 trials**.

## Ambiguities resolved

- Classic SuperTrend on close (source input default), trend starts at 1; the four SMAs only draw.
- Same mechanics as #363807 with another source and defaults.
- `FREQ = "1min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
