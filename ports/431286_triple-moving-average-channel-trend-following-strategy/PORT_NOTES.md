# #431286 Triple Moving Average Channel Trend Following Strategy -> `fmz_431286_triple_ema_alignment`

- FMZ source id: 431286 (lineage).
- Source: https://www.fmz.com/strategy/431286 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-06 16:58:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA alignment |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity / close stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p2` [21, 34] x `p3` [50, 100]: **4 trials**; EMA 9 fixed.

## Ambiguities resolved

- TP / SL off (default). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
