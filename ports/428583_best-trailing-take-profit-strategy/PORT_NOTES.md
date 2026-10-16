# #428583 Best Trailing Take Profit Strategy -> `fmz_428583_best_trailing_profit_2d`

- FMZ source id: 428583 (lineage).
- Source: https://www.fmz.com/strategy/428583 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 10:28:54). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [1, 2] x `trigger_pct` [3, 5]: **4 trials**; defaults 1 / 3 (the source's); SMA 20 / 50 fixed.

## Ambiguities resolved

- The "trailing take profit" is a close signal on the bar's range (strategy.close, next open), as written: it fires when a high clears the previous ratchet (high + 1 %), after the 3 % trigger.
- barssince na before the first event; trigger flags reset on a trend change (end of bar, as written).
- strategy() commented out. REVERSAL INTENDED. 2-day blocks of broker days (worker A's convention); FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
