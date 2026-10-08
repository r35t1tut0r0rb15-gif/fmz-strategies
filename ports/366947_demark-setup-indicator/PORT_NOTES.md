# #366947 Demark Setup Indicator [CC] -> `fmz_366947_demark_setup_turn`

- Source: https://www.fmz.com/strategy/366947 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-31 19:29:50). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A15). Not run.

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

`length` [3, 4, 6, 9] = **4 trials**.

## Ambiguities resolved

- Repainting off: the series is read one bar back on historical bars ([1]); kept.
- nz() makes missing history 0 (counts as lower), as coded. fillna(0) here is that nz(), not a fill of bars.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "td_sequential"`.

## Marks (2026-10-07)

`none`
