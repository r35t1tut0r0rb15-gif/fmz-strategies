# #361532 MacD-Custom-Indicator-Multiple-Time-FrameAll-Available-Options -> `fmz_361532_macd_gap_side`

- Source: https://www.fmz.com/strategy/361532 (PineScript, ChrisMoody's CM_MacD_Ult_MTF with
  orders added; FMZ last modified 2022-05-06 21:35:07). Verbatim here as `original_source.md`.
  Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pine bar-close evaluation, next-open fills. |
| 2 | ADAPT | Gap of 90 price units -> `gap_atr` x ATR(14). |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`gap_atr` [0.1, 0.25, 0.5] x `fast` [8, 12] x `slow` [26, 34] = **12 trials**. Signal SMA 9 fixed.

## Ambiguities resolved

- 90 USD on 2021-22 BTC hourly bars was roughly a quarter of an hourly ATR; `gap_atr` 0.25 is the
  declared stand-in, bracketed by the grid.
- The signal line is an SMA of MACD (as written), not an EMA.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
