# #426929 Super BitMoon Quantitative Momentum Trading Strategy -> `fmz_426929_super_bitmoon_long`

- Source: https://www.fmz.com/strategy/426929 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-15 16:13:05). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pd` [10, 22] x `rsi_len` [10, 14]: **4 trials**, defaults 10 / 10 (the source's); ATR stop 5 x 1, band 2 x 0.01, RSI level 50 fixed.

## Ambiguities resolved

- Direction 1 (long): short entries only close longs. Long only.
- Same bar: from flat the entry stands; while long the close goes flat.
- Pine population stdev; date range always true.
- FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
