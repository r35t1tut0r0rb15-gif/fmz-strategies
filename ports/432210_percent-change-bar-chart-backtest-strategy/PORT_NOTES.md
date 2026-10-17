# #432210 Percent Change Bar Chart Backtest Strategy -> `fmz_432210_percent_change_zones`

- FMZ source id: 432210 (lineage).
- Source: https://www.fmz.com/strategy/432210 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-15 15:41:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Percent-change zones |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`zone` [0.33, 1.0] x `lookback` [1, 3]: **4 trials**; the zones symmetric as in the defaults.

## Ambiguities resolved

- Percent zones as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
