# #427449 TEMA-DEMA-HMA Trend Following Strategy -> `fmz_427449_tema_dema_hma`

- FMZ source id: 427449 (lineage).
- Source: https://www.fmz.com/strategy/427449 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 10:56:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | No exchange header. |
| 4 | DONE | 100 % of equity, commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`t_length` [8, 13] x `d_length` [43, 21] x `h_length` [52, 26]: **8 trials**; defaults 8 / 43 / 52 (the source's); rising test 2 fixed. The bar size is the driver's.

## Ambiguities resolved

- No backtest header: `FREQ = "bar_size_pending"`, bars from `params["bar_size"]` (rule C3).
- REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`bar_size_pending`
