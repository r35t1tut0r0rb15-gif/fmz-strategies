# #361839 MAGIC-MACD -> `fmz_361839_macd_cross_reverse_1h`

- Source: https://www.fmz.com/strategy/361839 (PineScript v5, author ChaoZhang (HARI KRISHNA indicator), FMZ last
  modified 2022-05-08 17:16:51). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MACD cross only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same rule as #356844 (MACD 12/26/9 cross) but on 1-hour bars and with `ta.crossover` (<=) instead of a strict previous-bar test; not an exact duplicate, so ported. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12, 16] x `slow` [21, 26, 34] = **9 trials**. Signal 9 fixed.

## Ambiguities resolved

- The indicator's own MACD (5/50/30 on ohlc4) does not drive the orders.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
