# #363749 Fibonacci Progression With Breaks [LUX] -> `fmz_363749_fibonacci_progression_breaks`

- Source: https://www.fmz.com/strategy/363749 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-17 10:41:56). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A10). Not run.

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

`size` [0.5, 1.0, 2.0] x `seq_len` [2, 3, 4] = **9 trials**. ATR length 200 stays at the original.

## Ambiguities resolved

- ATR method (default) only; the Manual method uses price units and is not the default.
- Before ATR(200) exists the level holds the first close.
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks (2026-10-07)

`none`
