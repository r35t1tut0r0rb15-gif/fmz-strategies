# #365719 Pivot Based Trailing Maxima & Minima [LUX] -> `fmz_365719_lux_pivot_reverse`

- Source: https://www.fmz.com/strategy/365719 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-25 18:18:49). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

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

`length` [5, 10, 14, 20] = **4 trials**.

## Ambiguities resolved

- Pivots confirmed `length` bars later (no look-ahead); a 0 pivot counts as none.
- Trailing max/min/avg lines only draw.
- Daily bars are broker days (17:00 New York), `FREQ = "1D"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
