# #435520 HYE Mean Reversion SMA Strategy -> `fmz_435520_hye_two_offset_mean_reversion`

- FMZ source id: 435520 (lineage).
- Source: https://www.fmz.com/strategy/435520 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 16:51:23). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average offsets and an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`direction` ["Long Only", "Both"] x `pct_below` [3, 5]: **4 trials**; SMA 2 / 5, RSI 2 and the 3 % upper offset fixed.

## Ambiguities resolved

- Direction input in the grid. REVERSAL INTENDED (Both). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
