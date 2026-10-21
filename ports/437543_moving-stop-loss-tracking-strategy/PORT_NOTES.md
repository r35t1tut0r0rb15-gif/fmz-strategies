# #437543 Moving Stop Loss Tracking Strategy -> `fmz_437543_stoch_cross_pivot_stop`

- FMZ source id: 437543 (lineage).
- Source: https://www.fmz.com/strategy/437543 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 16:15:29). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Stochastic levels; the pivot stop and tick target are pending |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick target input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_k` [13, 9] x `smooth_k` [4, 3]: **4 trials**; D 3 and the 80 / 20 limits fixed; the stop is pending.

## Ambiguities resolved

- Pivot-moved stop and 400-tick target pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop_pending`
