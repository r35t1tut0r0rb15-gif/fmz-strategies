# #429953 Snap Back Moving Average Counter trend Strategy -> `fmz_429953_snap_back_ma_stack_long`

- FMZ source id: 429953 (lineage).
- Source: https://www.fmz.com/strategy/429953 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-23 15:31:21). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Moving-average order, a percentage gap and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The exit options stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gap` [0.02, 0.01] x `sl_pct` [4.0, 2.0]: **4 trials**; MA lengths and the 6 % target fixed.

## Ambiguities resolved

- Default exit option only. Long only. Mark coarse_bar_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop`
