# #361689 TMA-Overlay -> `fmz_361689_three_line_strike_faded`

- Source: https://www.fmz.com/strategy/361689 (PineScript v4, FMZ last modified 2022-05-07 21:08:06).
  Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Candle pattern on completed bars. |
| 2 | PASS | Candle colours and opens only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | No order inputs; declared starting variants. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`n_bars` [2, 3, 4] = **3 trials** (3 is the source's pattern).

## Ambiguities resolved

- **Direction as written**: the "bullish 3-line strike" sends a short and the bearish one a long.
- The smoothed MAs (21/50/100/200) and EMA(2) are drawn but not used by the orders.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
