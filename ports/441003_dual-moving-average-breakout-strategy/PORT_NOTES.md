# #441003 Dual Moving Average Breakout Strategy -> `fmz_441003_close_sma20_or_sma60_cross_own_exit_long`

- FMZ source id: 441003 (lineage).
- Source: https://www.fmz.com/strategy/441003 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 16:06:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_a` [20, 10] x `len_b` [60, 120]: **4 trials**.

## Ambiguities resolved

- One long at a time (default pyramiding), closed by its own average. Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
