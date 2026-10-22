# #446461 Gaussian Channel Adaptive Moving Average Strategy -> `fmz_446461_gaussian_channel_upper_break_long`

- FMZ source id: 446461 (lineage).
- Source: https://www.fmz.com/strategy/446461 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-28 18:08:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the recursive filter uses past values only |
| 2 | PASS | Gaussian channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored; the commission is a cost, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND446461. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`poles` [4, 2] x `period` [144, 72]: **4 trials**; the TR multiplier fixed.

## Ambiguities resolved

- nz() seeds as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
