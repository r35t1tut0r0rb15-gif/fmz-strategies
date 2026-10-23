# #129078 Relative Strength Strategy Based on Price -> `fmz_129078_volume_weighted_bar_location_ma100_break_range_stop_reversal`

- FMZ source id: 129078 (lineage).
- Source: https://www.fmz.com/strategy/129078 (MyLanguage, author 阿基米德的浴缸, FMZ last
  modified 2018-12-18 10:25:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stops against the signal close |
| 2 | PASS | Volume-weighted bar-location ratios with MA side and range breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [100, 50] x `m` [2.0, 3.0]: **4 trials**.

## Ambiguities resolved

- Statement order without AUTOFILTER; adds move BKPRICE. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
