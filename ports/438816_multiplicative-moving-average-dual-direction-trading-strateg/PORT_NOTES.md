# #438816 Multiplicative Moving Average Dual direction Trading Strategy -> `fmz_438816_pmax_cross_long`

- FMZ source id: 438816 (lineage).
- Source: https://www.fmz.com/strategy/438816 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 14:50:32). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average and ATR stop line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND365691. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [3.0, 2.0] x `length` [10, 20]: **4 trials**; ATR 10 and hl2 fixed.

## Ambiguities resolved

- Long only (long-short off). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
