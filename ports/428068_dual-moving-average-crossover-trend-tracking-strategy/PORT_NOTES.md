# #428068 Dual Moving Average Crossover Trend Tracking Strategy -> `fmz_428068_ema_10_20_cross`

- FMZ source id: 428068 (lineage).
- Source: https://www.fmz.com/strategy/428068 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 11:52:16). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the daily / weekly Heikin Ashi securities are drawn only. |
| 2 | PASS | EMA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`par1` [10, 5] x `par2` [20, 50]: **4 trials**; defaults 10 / 20 (the source's).

## Ambiguities resolved

- Heikin Ashi securities and the other EMAs reach no order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
