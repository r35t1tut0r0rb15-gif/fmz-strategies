# #439987 Quantitative Strategy Based on Exponential Moving Average and Volume Weighting -> `fmz_439987_exp_volume_weighted_average_vs_prev_close_1h_reversal`

- FMZ source id: 439987 (lineage).
- Source: https://www.fmz.com/strategy/439987 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-25 15:31:21). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against its exponential volume-weighted average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [22, 50]: **2 trials**.

## Ambiguities resolved

- Position follows the state. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_weighted_ma"`.

## Marks

`none`
