# #438499 Trend Following Strategy Based on Moving Average Difference -> `fmz_438499_devick_turns_17utc_close`

- FMZ source id: 438499 (lineage).
- Source: https://www.fmz.com/strategy/438499 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 14:42:06). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed EMA difference turns; a UTC clock close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [21, 34] x `close_hour` [17, 21]: **4 trials**.

## Ambiguities resolved

- 17:00 UTC close_all after the entries (as #430380). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
