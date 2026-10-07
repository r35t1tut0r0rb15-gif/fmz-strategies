# #363824 Momentum-based ZigZag -> `fmz_363824_qqe_momentum_zigzag`

- Source: https://www.fmz.com/strategy/363824 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-17 16:29:07). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`rsi_len` [9, 14, 21] x `qqe_factor` [3.0, 4.238] = **6 trials**. RSI smoothing 5 and RSI(5) 80/20 stay at the originals.

## Ambiguities resolved

- Momentum selector default "QQE"; MACD and MovingAverage modes are not ported.
- qqe_goingup/down use the flips up to the previous bar (counters updated later in the bar), as coded; barssince of a never-true condition is na.
- Zigzag, stop levels and alert texts do not reach the orders.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
