# #428970 双色K线追踪策略Dual-Color-K-line-Tracking-Strategy -> `fmz_428970_noro_candles`

- FMZ source id: 428970 (lineage).
- Source: https://www.fmz.com/strategy/428970 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-11 14:53:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle colours only. |
| 3 | PASS | Spot pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bq` [2, 3]: **2 trials**.

## Ambiguities resolved

- The date-window close-all dropped; colour-change exits kept. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
