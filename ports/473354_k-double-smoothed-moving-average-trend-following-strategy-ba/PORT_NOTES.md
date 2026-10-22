# #473354 双重平滑平均线趋势跟踪策略-基于改良型平安江氏K线-Double-Smoothed-Moving-Average-Trend-Following-Strategy-Based-on-Modified-Heikin-Ashi -> `fmz_473354_smoothed_heikin_ashi_colour_change_delayed_long`

- FMZ source id: 473354 (lineage).
- Source: https://www.fmz.com/strategy/473354 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:03:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed Heikin-Ashi colour changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [10, 20] x `len2` [10, 20]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
