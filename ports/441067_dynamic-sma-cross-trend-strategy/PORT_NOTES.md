# #441067 Dynamic SMA Cross Trend Strategy -> `fmz_441067_sma7_30_cross_long`

- FMZ source id: 441067 (lineage).
- Source: https://www.fmz.com/strategy/441067 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 12:14:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C145). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The ATR risk quantity and percent-of-equity default stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [7, 14] x `medium` [30, 60]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
