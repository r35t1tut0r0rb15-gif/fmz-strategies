# #361565 Monthly-Returns-in-PineScript-Strategies -> `fmz_361565_pivot_flag_market_reverse`

- Source: https://www.fmz.com/strategy/361565 (PineScript v4, FMZ last modified 2022-05-08 10:43:41).
  Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Market entries at bar close; pivots confirmed `rightBars` later. |
| 2 | PASS | Pivot levels come from the bars. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | The commented `strategy()` line's 25 % of equity is not active; nothing else. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | The name is about a returns table, not used. |

## Declared grid (criterion 5)

`left_bars` [2, 3, 5] x `right_bars` [1, 2, 3] = **9 trials**.

## Ambiguities resolved

- **As written vs the classic**: TradingView's Pivot Reversal strategy enters with `stop=` orders
  at the pivot; this copy has no `stop=`, so it enters at market the bar after the flag is set
  (long after a pivot HIGH, i.e. not a breakout). Ported as written; rule 5 does not apply (no
  `stop=`/`limit=` in the source). Flagged in the worker report.
- Pivot test strict on both sides (Pine's tie rule is not documented).
- `FREQ = "12h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
