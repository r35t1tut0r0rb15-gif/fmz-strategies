# #427391 Trend Following Strategy Based on Price Friction Zones -> `fmz_427391_lube_price_friction`

- FMZ source id: 427391 (lineage).
- Source: https://www.fmz.com/strategy/427391 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 16:46:17). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts, linear filter. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Leverage / contracts stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`barsback` [500, 200] x `range` [100, 50] x `tlevel` [-10, 0]: **8 trials**; defaults 500 / 100 / -10 (the source's); friction level 50 fixed.

## Ambiguities resolved

- Friction counts the previous 500 bars against the current close; thresholds 5 bars back, as written.
- `end` (friction above the mid level) closes either side. barcount > 20 skips the first bars.
- REVERSAL INTENDED. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
