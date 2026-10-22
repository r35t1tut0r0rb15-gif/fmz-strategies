# #473402 Statistical Deviation Based Market Extreme Drawdown Strategy -> `fmz_473402_drawdown_1sd_below_mean_hold35_long`

- FMZ source id: 473402 (lineage).
- Source: https://www.fmz.com/strategy/473402 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:46:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Drawdown-deviation entries with a time exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [50, 100] x `threshold` [-1.0, -2.0] x `exit_bars` [35, 20]: **8 trials**; the stdev length 50.

## Ambiguities resolved

- Hold counted from the signal bar, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
