# #439985 Origix Ashi Strategy Based on Smoothed Moving Average -> `fmz_439985_origix_smoothed_ha_close_long`

- FMZ source id: 439985 (lineage).
- Source: https://www.fmz.com/strategy/439985 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 15:26:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against a smoothed blend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smoothed_ha_length` [10, 20, 5]: **3 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
