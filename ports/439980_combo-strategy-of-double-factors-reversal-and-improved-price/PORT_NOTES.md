# #439980 Combo Strategy of Double Factors Reversal and Improved Price Volume Trend -> `fmz_439980_reversal123_modified_pvt_combo_15m_reversal`

- FMZ source id: 439980 (lineage).
- Source: https://www.fmz.com/strategy/439980 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-25 14:46:36). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Combined price-pattern and price-volume-trend states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `pvt_len` [23, 50]: **4 trials**; K smoothing 1, D 3, level 50.

## Ambiguities resolved

- Volume scale and level cancel in the SMA comparison. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "hpotter_combo"`.

## Marks

`none`
