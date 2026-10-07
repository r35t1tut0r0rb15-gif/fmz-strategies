# #194224 MACD低买高卖自动跟单滑动止损 -> `fmz_194224_macd_hist_turn_long`

- Source: https://www.fmz.com/strategy/194224 (JavaScript, author John。, FMZ last modified
  2020-04-20 11:54:46). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming bar; the port evaluates on completed bars. Exits that read ticker.Last use the bar close. |
| 2 | ADAPT | 0.5 price-unit candle margins -> `body_atr` x ATR; histogram threshold `ac1` -> `hist_atr` x ATR; 50 % loss exit -> `stop_atr` x ATR. |
| 3 | PASS (screen: REVIEW) | Spot buy/sell only. |
| 4 | DONE | Buy with the whole balance in slices with timeouts, `SlidePrice`, `MinStock`, sell loop -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`hist_atr` [0, 0.05, 0.1] x `body_atr` [0.1, 0.25, 0.5] x `stop_atr` [5, 10, 20] = **27 trials**.
MACD 12/26/9 fixed.

## Ambiguities resolved

- "TrailingStop" is a fixed loss threshold from the buy price, not a trailing stop, so no
  `trailing_stop_pending` mark; it is a close condition -> exit signal (rule 3 by analogy).
- 50 % of price has no stable ATR equivalent; `stop_atr` 10 is a declared stand-in for a very
  wide disaster exit, bracketed by the grid.
- No bar size in the source: `FREQ = "bar_size_pending"`, mark `bar_size_pending` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`: MACD histogram turning positive above the zero line.

## Marks (2026-10-07)

`bar_size_pending`
