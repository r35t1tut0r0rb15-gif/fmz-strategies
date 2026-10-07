# #362898 RSI by zdmre -> `fmz_362898_rsi_extreme_cross_momentum`

- Source: https://www.fmz.com/strategy/362898 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-13 16:47:24). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A9). Not run.

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

`rsi_len` [7, 14, 21] = **3 trials**. Levels 70/30 stay at the originals.

## Ambiguities resolved

- `cross(rsi, 70) and rsi >= 70` is the upward cross only; `os` the downward cross through 30.
- Long on the overbought cross, short on the oversold cross: kept as written.
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
