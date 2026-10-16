# #428081 Dual Momentum Strategy -> `fmz_428081_dual_momentum_sign`

- FMZ source id: 428081 (lineage).
- Source: https://www.fmz.com/strategy/428081 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 15:03:57). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Momentum signs only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity quantity and the off stop stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_period` [5, 10] x `slow_period` [10, 20]: **4 trials**; defaults 5 / 10 (the source's).

## Ambiguities resolved

- Long-only off and stop off (defaults). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
