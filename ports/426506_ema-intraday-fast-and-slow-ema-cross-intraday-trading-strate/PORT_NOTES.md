# #426506 Fast and Slow EMA Cross Intraday Trading Strategy -> `fmz_426506_ema_110_40_cross_stop`

- Source: https://www.fmz.com/strategy/426506 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-12 16:28:09). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Tick distance -> ATR(14) multiple at the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.25, 1.0, 2.0]: **3 trials**, EMA 110 / 40 fixed (the source's). The default 0.25 is the smallest step (500 ticks is a fraction of an hourly ATR).

## Ambiguities resolved

- "Fast" 110 is longer than "slow" 40, as written.
- Criterion 2 (ADAPT): 500 ticks -> sl_atr x ATR(14) at the signal bar.
- Crosses alternate: after a stop the next entry is the opposite cross, no mirroring needed.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
