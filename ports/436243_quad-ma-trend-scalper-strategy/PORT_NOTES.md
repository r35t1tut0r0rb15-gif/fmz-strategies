# #436243 Quad MA Trend Scalper Strategy -> `fmz_436243_quad_ma_trend_scalper`

- FMZ source id: 436243 (lineage).
- Source: https://www.fmz.com/strategy/436243 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-22 14:25:04). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The pyramiding input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length1` [13, 8] x `length2` [21, 34]: **4 trials**; EMA 54 / 84 fixed.

## Ambiguities resolved

- Pyramiding not ported; orders in call order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
