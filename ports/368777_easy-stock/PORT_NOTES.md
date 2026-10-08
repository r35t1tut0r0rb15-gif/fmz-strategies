# #368777 Easy stock -> `fmz_368777_linreg_vs_weekly_hull`

- Source: https://www.fmz.com/strategy/368777 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-12 21:13:20). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A16). Not run.

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

`length` [12, 24, 36] x `len` [50, 100] = **6 trials**. Weekly timeframe and shift 1 stay at the originals.

## Ambiguities resolved

- Weekly bars built from the 4 h bars (weeks from Monday 00:00 UTC); lookahead off = last completed week, whose value is hma3 one week earlier ([shift] inside the request).
- v4 integer division: p = 12, p/3 = 4, p/2 = 6. The other weekly HMA only draws.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks (2026-10-07)

`none`
