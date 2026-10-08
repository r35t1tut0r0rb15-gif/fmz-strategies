# #426816 MACD Moving Average Crossover Strategy -> `fmz_426816_macd_above_signal_long`

- Source: https://www.fmz.com/strategy/426816 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 17:03:47). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A26). Not run.

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

`fast` [12, 8] x `slow` [26, 21] x `exit_pair` [(9, 26), (5, 20)]: **8 trials**, defaults 12 / 26 / (9, 26) (the source's); signal 9 fixed.

## Ambiguities resolved

- As written `(longCondition)` and `(SMacdcondition)` are bare statements: entry = MACD above signal, exit = SMA 9 under SMA 26 (decision owed: likely meant `and`).
- Date window dropped. Same bar: from flat the entry stands; while long the close goes flat.
- Long only. FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
