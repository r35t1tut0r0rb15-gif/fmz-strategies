# #402455 顶/底背离指标观察系统 with 止盈止损 -> `fmz_402455_macd_zero_cross_bracket`

- Source: https://www.fmz.com/strategy/402455 (PineScript v5, author Zer3192, FMZ last
  modified 2023-03-02 22:39:32). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A18). Not run.

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

`stop_pct` [1, 5, 99] (99 = the header args) x `tp_pct` [1, 3, 5] = **9 trials**.

## Ambiguities resolved

- Defaults are input() defaults (1 % / 1 %); the header args (stop 99 %) are in the grid.
- Fixed fractions on the entry price -> sl/tp stops; daily bars: `coarse_bar_stop`.
- Daily bars are broker days (17:00 New York), `FREQ = "1D"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`coarse_bar_stop`
