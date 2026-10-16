# #427436 Moving Average Crossover Strategy -> `fmz_427436_sma_13_144_long`

- FMZ source id: 427436 (lineage).
- Source: https://www.fmz.com/strategy/427436 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 10:28:27). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma` [13, 21] x `slow_ma` [144, 89] x `ma_type` [1 SMA, 2 EMA]: **8 trials**; defaults 13 / 144 / SMA (the source's).

## Ambiguities resolved

- `time > finish` (2020-01-01) in the close is the author's window end: dropped.
- Long only. FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
