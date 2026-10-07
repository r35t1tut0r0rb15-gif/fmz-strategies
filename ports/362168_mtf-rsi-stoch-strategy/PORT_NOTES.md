# #362168 MTF-RSI-STOCH-Strategy -> `fmz_362168_mtf_rsi_stoch_average`

- Source: https://www.fmz.com/strategy/362168 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-10 12:06:12). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Higher timeframes read as completed bars; lower ones as the day's last bars; decisions at the daily close. |
| 2 | PASS | Oscillator levels only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [9, 14, 21] x `k_len` [9, 14, 21] = **9 trials**. Levels 30/70 (RSI), 30/70 (stoch), exits 70/50 fixed.

## Ambiguities resolved

- Weekly values exclude the week that ends on the decision day (one-day lag on that day only).
- `FREQ = "1h"` is the module's bar size; decisions are daily at 17:00 New York (backtest period 1d).
- The 80/20 'General' levels are plot-only inputs.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
