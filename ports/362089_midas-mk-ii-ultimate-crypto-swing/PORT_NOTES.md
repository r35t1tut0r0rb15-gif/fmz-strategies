# #362089 Midas-Mk-II-Ultimate-Crypto-Swing -> `fmz_362089_ema_sma_cross_macd_confirm`

- Source: https://www.fmz.com/strategy/362089 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 23:22:05). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Average crosses and histogram signs. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | The name's claim is not used. |

## Declared grid (criterion 5)

`ema_len` [13, 21, 34] x `sma_len` [34, 55, 89] = **9 trials**. MACD 55/89/9 fixed.

## Ambiguities resolved

- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
