# #362403 BB-RSI-ADX-Entry-Points -> `fmz_362403_bb_touch_rsi_adx`

- Source: https://www.fmz.com/strategy/362403 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-11 12:42:28). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders on the bar's high/low. |
| 2 | PASS | Bands, %B, RSI and ADX levels. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [9, 20] x `adx_min` [20, 25, 30] = **6 trials**. RSI windows 30-50 / 50-70 fixed.

## Ambiguities resolved

- `%B` uses the 1-stdev bands (stDev - 1), as written.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`
