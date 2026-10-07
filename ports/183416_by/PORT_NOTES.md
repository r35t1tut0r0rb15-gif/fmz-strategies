# #183416 定量分型速率交易策略-by泊宇量化 -> `fmz_183416_channel_mid_slope_reverse`

- Source: https://www.fmz.com/strategy/183416 (MyLanguage, author homily, FMZ last modified
  2021-02-08 13:47:31). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model, completed bars. |
| 2 | PASS | Only the direction of change of the slope is used. |
| 3 | PASS | OKEx quarterly contract in the header only. |
| 4 | DONE | `liang` lot formula (and 2x lots on shorts) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`length` [20, 35, 50] x `smooth` [3, 5, 8] = **9 trials**.

## Ambiguities resolved

- `SLOPE(X,N)` = least-squares slope over the last N bars including the current one.
- Always in the market after the first signal; reverses whenever the slope turns.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "slope_momentum"`: trades the change in a regression slope.

## Marks (2026-10-07)

`none`
