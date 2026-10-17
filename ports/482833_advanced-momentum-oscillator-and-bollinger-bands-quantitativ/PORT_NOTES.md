# #482833 基于动量振荡与布林带的高级量化策略系统-Advanced-Momentum-Oscillator-and-Bollinger-Bands-Quantitative-Strategy-System -> `fmz_482833_bb_cmo_extreme_reentry_2d`

- FMZ source id: 482833 (lineage).
- Source: https://www.fmz.com/strategy/482833 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:50:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands and the CMO. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.0, 1.5] x `cmo_level` [50, 40]: **4 trials**; defaults 2 / 50 (the source's); BB 20 and CMO 14 fixed.

## Ambiguities resolved

- The closes follow the entries in the script: they act on the position held at the bar's start and never undo an
  entry on that bar (#430850). Exits are emitted only on going flat.
- `ta.stdev` is the population deviation; `ta.cmo` uses plain sums.
- REVERSAL INTENDED. Two-day bars: blocks of broker-day dates from 1970-01-01 (decision owed, #426509).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
