# #363590 RSI MTF Ob+Os -> `fmz_363590_rsi_mtf_extreme_momentum`

- Source: https://www.fmz.com/strategy/363590 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-16 18:17:17). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`rsi_len` [9, 14, 21] = **3 trials**. Levels 65/35 and the five timeframes stay at the originals.

## Ambiguities resolved

- Each RSI is the last completed block as seen by the previous chart bar (`lookahead_off` + `[1]`); blocks built from 15 m bars, floored on UTC.
- Overbought on all timeframes enters long, oversold short: kept as written.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
