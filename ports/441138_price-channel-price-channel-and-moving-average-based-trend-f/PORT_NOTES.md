# #441138 基于Price-Channel和均线的趋势跟踪策略Price-Channel-and-Moving-Average-Based-Trend-Following-Strategy -> `fmz_441138_noro_channel_distance_bands_reversal`

- FMZ source id: 441138 (lineage).
- Source: https://www.fmz.com/strategy/441138 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-06 09:46:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C147). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price-channel distance bands and candle colours |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND441138. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
