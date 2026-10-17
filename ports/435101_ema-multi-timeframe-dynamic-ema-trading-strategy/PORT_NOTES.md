# #435101 多个EMA周期动态交易策略Multi-Timeframe-Dynamic-EMA-Trading-Strategy -> `fmz_435101_ema_fan_pair_cross_long`

- FMZ source id: 435101 (lineage).
- Source: https://www.fmz.com/strategy/435101 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-12 12:18:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the exit follows the opening entry (tracked) |
| 2 | PASS | Average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1 / (close x count) quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`first` [8, 5]: **2 trials**; the fan's other lengths fixed (13 ... 233).

## Ambiguities resolved

- Exit tied to the opening pair; the author's date window (finish 2020) dropped. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
