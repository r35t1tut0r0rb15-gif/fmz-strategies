# #425773 EMA-Cross-JC Intraday with Trailing SL -> `fmz_425773_ema_cross_intraday_bracket`

- Source: https://www.fmz.com/strategy/425773 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-04 15:39:54). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Stop 100 / target 200 price units -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG425773` (Jaccard >= 0.80) with #425776 (DUPLICATE); best Jaccard 0.914 with #425776. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [15, 26] x `fast` [5, 9] x `sl_atr` [1.0, 2.0] (target = 2 x stop, the source ratio) = **8 trials**.

## Ambiguities resolved

- Stop 100 / target 200 price units -> `sl_atr` / 2 `sl_atr` x ATR(14) at the signal bar (criterion 2).
- Square-off at 15:20 exchange time (UTC for the Binance pair): entries only before, exits from then on (close_all).
- trailingStop is never set (na), so the trailing exit does nothing; TSI filter commented out.
- `FREQ = "45min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
