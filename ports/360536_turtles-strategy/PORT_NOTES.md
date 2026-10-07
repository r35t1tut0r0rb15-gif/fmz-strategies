# #360536 海龟交易法Turtles-strategy -> `fmz_360536_turtle_20_55_pine`

- Source: https://www.fmz.com/strategy/360536 (PineScript, FMZ last modified 2022-05-21 20:43:32).
  Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close rules on high/low with market orders. |
| 2 | PASS | Channels in bars, distances in N (ATR). |
| 3 | PASS | Bitfinex spot pair in the header only. |
| 4 | DONE | `RiskRatio`, unit size from equity/N, `ContractUnit`, `MinStock`, pyramiding 4 -> `original_sizing.txt`. Adds kept only as the stop reference. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same system as the MyLanguage turtle #126968 (rules differ in details: entries on high/low, not close). |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`bo_length` [10, 20, 30] x `fs_length` [40, 55, 80] x `te_length` [5, 10, 15] = **27 trials**.
ATR 20, 2N stop, 0.5N add, last-trade filter on: fixed (original values).

## Ambiguities resolved

- `PreBreakoutFailure` starts false, so with the filter on the first trades come only from the
  55-bar channel until a stop-loss exit has happened (as written).
- Stop and channel exits use the bar's low/high at the close and fill at the next open.
- `FREQ = "1D"` broker days from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`none`
