# #428810 Moving Average Crossover Multi Timeframe Strategy -> `fmz_428810_ema15_30_cross_mtf`

- FMZ source id: 428810 (lineage).
- Source: https://www.fmz.com/strategy/428810 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-09 16:41:04). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average crosses only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity, the pyramiding counters and the off-by-default exits stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [15, 10] x `slow` [30, 50]: **4 trials**; EMA type, close source, same resolution fixed.

## Ambiguities resolved

- Off-by-default exits not ported. Default MA type only. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
