# #438500 Quantitative Trading Strategy Quantity Trend Tracking Opening -> `fmz_438500_day_change_volume_vs_day_average_volume_surge_30m_reversal`

- FMZ source id: 438500 (lineage).
- Source: https://www.fmz.com/strategy/438500 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 14:46:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Intraday change-weighted volume against its day average with a volume surge |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_len` [20, 40]: **2 trials**; day average since the day began.

## Ambiguities resolved

- Previous broker day's close; day average as written; mintick rounding left out. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`none`
