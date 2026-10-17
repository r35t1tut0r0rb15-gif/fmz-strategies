# #489009 多重动态指标组合策略-Multi-Dynamic-Indicator-Combination-Strategy -> `fmz_489009_supertrend_flip_bb_take_profit_2d`

- FMZ source id: 489009 (lineage).
- Source: https://www.fmz.com/strategy/489009 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 10:12:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR stops and bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_length` [22, 10] x `st_mult` [3.0, 2.0]: **4 trials**; defaults 22 / 3 (the source's); BB 20 x 2 (SMA) and
wicks on fixed.

## Ambiguities resolved

- The SuperTrend as written (wicks, doji keeps the stop). The band closes act on the position held at the bar's
  start. The VWMA basis option (volume) is not used (check 8).
- Two-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
