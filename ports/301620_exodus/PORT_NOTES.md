# #301620 三均线系统Exodus -> `fmz_301620_ema_cross_macd_confirm`

- Source: https://www.fmz.com/strategy/301620 (JavaScript, author Exodus[策略代写], FMZ last
  modified 2021-11-28 07:20:15). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Runs once per bar just after it opens; the port evaluates on completed bars. |
| 2 | ADAPT | 1 % stop / 5 % target -> `stop_atr` x ATR(14) and `win_loss` x that distance. |
| 3 | PASS (screen: REVIEW) | Binance USDT swap is the venue only. |
| 4 | DONE | Fixed `buyVolume` -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | The description's backtest pictures are not used. |

## Declared grid (criterion 5)

`within` [2, 4, 8] x `stop_atr` [1, 2, 3] x `win_loss` [2, 5] = **18 trials**. EMA 8/34 and
MACD 16/26/9 fixed.

## Ambiguities resolved

- `stopLossRate` default `true` = 1 (%).
- The stop and target are checked once per bar on the current price -> close conditions.
- The cross-window test uses hours; at the 60-minute default it equals bars.
- `FREQ = "1h"`: `GetRecords(PERIOD_M1 * period)` with `period` = 60.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`: EMA cross with MACD confirmation.

## Marks (2026-10-07)

`none`
