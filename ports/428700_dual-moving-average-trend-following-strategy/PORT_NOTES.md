# #428700 Dual Moving Average Trend Following Strategy -> `fmz_428700_two_midpoint_trends`

- FMZ source id: 428700 (lineage).
- Source: https://www.fmz.com/strategy/428700 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-08 14:25:40). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Price vs channel midpoints only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() capital, cash quantity, slippage and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p1` [14, 10] x `p2` [21, 30]: **4 trials**.

## Ambiguities resolved

- The channel includes the current bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
