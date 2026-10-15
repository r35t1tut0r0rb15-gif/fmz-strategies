# #427164 Moving Average Crossover Strategy -> `fmz_427164_price_ma_cross`

- FMZ source id: 427164 (lineage).
- Source: https://www.fmz.com/strategy/427164 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-18 17:35:37). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C2). Not run.
- Near-duplicate group: **DG427164** (with #437546, Jaccard 0.971); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 50 % of equity per unit, pyramiding 2 stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427164. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1_len` [20, 10] x `ma2_len` [30, 50] x `ma_type` [1 SMA, 2 EMA]: **8 trials**; defaults 20 / 30 / SMA (the source's); the cross conditions are the defaults ("price x MA1" long, "price x MA2" short).

## Ambiguities resolved

- pyramiding 2 adds are sizing; one position.
- Date-window inputs are the author's backtest window; `in_time` is the constant true.
- REVERSAL INTENDED. FREQ = "10min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
