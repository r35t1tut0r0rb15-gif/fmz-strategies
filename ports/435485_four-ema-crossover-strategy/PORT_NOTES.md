# #435485 Four EMA Crossover Strategy -> `fmz_435485_four_ema_same_bar_cross`

- FMZ source id: 435485 (lineage).
- Source: https://www.fmz.com/strategy/435485 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 11:55:36). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast1` [9, 5] x `slow2` [200, 100]: **4 trials**; EMA 21 and EMA 50 fixed.

## Ambiguities resolved

- Same-bar double cross as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
