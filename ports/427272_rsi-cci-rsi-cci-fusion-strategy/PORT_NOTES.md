# #427272 RSI-CCI Fusion Strategy -> `fmz_427272_rsi_cci_fusion`

- FMZ source id: 427272 (lineage).
- Source: https://www.fmz.com/strategy/427272 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-19 16:42:18). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; strategy() commented out (Pine defaults). |
| 2 | PASS | Rolling z-scores (dimensionless). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `rsi_weight` [0.5, 0.8] x `enable_short` [False, True]: **8 trials**; defaults 14 / 0.5 / False (the source's).

## Ambiguities resolved

- All statistics are rolling 14-bar windows ending at the bar (no whole-series figure); population stdev; CCI with mean absolute deviation.
- Long only by default; with shorts on the crosses reverse (REVERSAL INTENDED).
- FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks

`none`
