# #186598 海龟策略btc现货版 -> `fmz_186598_spot_turtle_breakout`

- Source: https://www.fmz.com/strategy/186598 (Python, author groot, FMZ last modified
  2020-03-06 12:04:41). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming daily bar once a day; the port evaluates on completed bars. |
| 2 | PASS | Channels in bars, distances in ATR. |
| 3 | PASS | OKEX spot in the header only. |
| 4 | DONE | Unit = 1 % of portfolio per ATR capped by balance, +10/+100 price offsets, order history frame -> `original_sizing.txt`. Adds kept only as the exit reference. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | The description's "80 % a year" is not used. |

## Declared grid (criterion 5)

`dc_range` [20, 30, 40] x `atr_length` [14, 24] x `stop_atr` [1.5, 2, 3] = **18 trials**.
The argument defaults are 30/24; the backtest header's args use 20/14; both are in the grid.

## Ambiguities resolved

- The channel windows skip the last completed bar ([-2]) as well as the forming one; reproduced.
- `fresh_rete` is both the bar length and the polling interval; at its default (24 h) the bars
  are daily, so `FREQ = "1D"` broker days (the backtest header also says `1d`).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`none`
