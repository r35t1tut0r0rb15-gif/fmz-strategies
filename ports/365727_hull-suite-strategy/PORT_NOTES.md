# #365727 Hull Suite Strategy -> `fmz_365727_hull_suite_slope`

- Source: https://www.fmz.com/strategy/365727 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-25 18:48:40). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | strategy() sizing / trade-size inputs -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365727` (Jaccard >= 0.80) with #434954 (DUPLICATE); best Jaccard 0.837 with #434954. Group `ND365727` (Jaccard 0.65-0.80) with #436100 (PORT_CANDIDATE); best Jaccard 0.652 with #436100. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 55, 89, 180] = **4 trials** (the source suggests 55 for swing, 180-200 for S/R).

## Ambiguities resolved

- Pine v4 integer division (55/2 -> 27). Direction input unused: allow_entry_in is commented out.
- Hull variation default Hma.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
