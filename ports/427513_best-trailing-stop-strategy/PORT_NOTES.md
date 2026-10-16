# #427513 Best Trailing Stop Strategy -> `fmz_427513_best_trailing_stop_2d`

- FMZ source id: 427513 (lineage).
- Source: https://www.fmz.com/strategy/427513 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 20:58:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; trail tested on completed bars (exit signal). strategy() commented out: no tick evaluation. |
| 2 | PASS | MA lengths, percent distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed qty / capital settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [3, 6] x `trigger_pct` [2, 4] x `slow` [45, 30]: **8 trials**; defaults 3 / 2 / 45 (the source's); SMA 15 fixed.

## Ambiguities resolved

- The trailing stop is `strategy.close` on a completed bar's cross of the ratchet line: an exit signal (rule 2), no mark (the line is on lows / highs, not the best price).
- The trigger flag is sticky until the trend changes; the reset comes after its use on the bar (script order).
- 2-day bars as worker A's #426995. REVERSAL INTENDED. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
