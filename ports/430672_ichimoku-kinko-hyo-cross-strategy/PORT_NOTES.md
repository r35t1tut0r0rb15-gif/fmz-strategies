# #430672 Ichimoku Kinko Hyo Cross Strategy -> `fmz_430672_ichimoku_basic_cloud`

- FMZ source id: 430672 (lineage).
- Source: https://www.fmz.com/strategy/430672 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-31 15:00:43). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Channel midpoints and momentum signs. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ts_bars` [9, 20] x `ks_bars` [26, 60]: **4 trials**; Senkou B 52 and offsets 26 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
