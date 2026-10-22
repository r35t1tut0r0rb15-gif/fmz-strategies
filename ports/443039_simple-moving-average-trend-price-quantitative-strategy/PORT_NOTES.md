# #443039 Simple Moving Average Trend Price Quantitative Strategy -> `fmz_443039_sma50_cross_outside_band_reversal`

- FMZ source id: 443039 (lineage).
- Source: https://www.fmz.com/strategy/443039 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-28 17:40:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings beyond the bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trend_period` [50, 20] x `bb_period` [20, 50]: **4 trials**; the deviation fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
