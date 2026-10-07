# #362167 EMA-AROON-ASH -> `fmz_362167_ema_aroon_ash_bracket`

- Source: https://www.fmz.com/strategy/362167 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-10 11:29:01). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; stop and target are resting orders fixed at entry (sl_stop/tp_stop). |
| 2 | ADAPT | 0.1 %-of-price stop buffer -> `buffer_atr` x ATR(14); the pivot itself is a bar level. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [100, 200] x `aroon_len` [14, 20, 30] x `tp_mult` [1.5, 2, 3] = **18 trials**. ASH 9/3, pivot lookback 20 fixed.

## Ambiguities resolved

- Stop/target levels from the signal bar's close are applied as fractions of the fill price (vbt).
- Only the default ASH mode (RSI, WMA) is ported.
- `FREQ = "3min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
