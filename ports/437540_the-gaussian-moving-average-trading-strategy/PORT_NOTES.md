# #437540 The Gaussian Moving Average Trading Strategy -> `fmz_437540_ha_zscore_percentile_cross`

- FMZ source id: 437540 (lineage).
- Source: https://www.fmz.com/strategy/437540 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-03 16:06:45). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Z-score against its own percentiles |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`z_len` [25, 50] x `pct_len` [50, 100]: **4 trials**; EMA 10 / 20 and the 100-bar extremes fixed.

## Ambiguities resolved

- Second long id with pyramiding 0; per-id closes; start window dropped. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
