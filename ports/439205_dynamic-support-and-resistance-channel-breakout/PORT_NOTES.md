# #439205 Dynamic Support and Resistance Channel Breakout -> `fmz_439205_pivot_channel_whole_bar_break_volume_osc_30m_reversal`

- FMZ source id: 439205 (lineage).
- Source: https://www.fmz.com/strategy/439205 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 12:30:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Whole-bar breaks of pivot levels on rising volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot_len` [15, 10] x `vol_thresh` [20, 10]: **4 trials**; left = right length.

## Ambiguities resolved

- Strict pivots; later call wins on a two-sided bar. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`none`
