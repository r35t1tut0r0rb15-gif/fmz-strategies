# #436787 Momentum Indicator Crossover Strategy -> `fmz_436787_ema_cross_body_reentry`

- FMZ source id: 436787 (lineage).
- Source: https://www.fmz.com/strategy/436787 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-27 17:04:33). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings and body comparison |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The unused position-size input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND435154. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [25, 15] x `len2` [100, 50]: **4 trials**.

## Ambiguities resolved

- entrybar carried as written (updated by every entry signal). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
