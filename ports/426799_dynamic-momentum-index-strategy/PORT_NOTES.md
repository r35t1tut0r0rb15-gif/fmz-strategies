# #426799 Dynamic Momentum Index Strategy -> `fmz_426799_cmo_disparity`

- Source: https://www.fmz.com/strategy/426799 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 16:15:42). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

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

`len_first` [100, 200] x `len_second` [50, 30] x `len_third` [20, 10]: **8 trials**, defaults 200 / 50 / 20 (the source's).

## Ambiguities resolved

- The -1 test comes first (short_first), as in the source.
- "Trade reverse" off.
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_reversion"`.

## Marks (2026-10-07)

`none`
