# #436120 The Multi Period Trading Strategy Based on Volatility Index and Stochastic Oscillator -> `fmz_436120_vix_fix_rebound_long`

- FMZ source id: 436120 (lineage).
- Source: https://www.fmz.com/strategy/436120 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 14:34:42). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Filters as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The pyramiding input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pd` [22, 30] x `ph` [0.85, 0.9]: **4 trials**; Bollinger 20 / 2, window 50 and the stochastic 14 / 3 / 3 fixed.

## Ambiguities resolved

- Pyramiding not ported; entry plus close on one bar: flat. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
