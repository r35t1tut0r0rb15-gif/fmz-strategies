# #427372 Renko Boxes and TEMA Indicator Micro-Profit Strategy -> `fmz_427372_tema_cross_micro_profit_long`

- FMZ source id: 427372 (lineage).
- Source: https://www.fmz.com/strategy/427372 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-20 14:36:46). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.
- Near-duplicate group: **ND427372** (with #439823, Jaccard 0.740); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; gain test on the close. |
| 2 | PASS | MA lengths, percent of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 100 with the averaging protection, qty 1, commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427372. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tema_length` [5, 9] x `smma_length` [30, 60] x `min_gain_pct` [2, 1]: **8 trials**; defaults 5 / 30 / 2 (the source's); SMA 3 fixed.

## Ambiguities resolved

- The averaging-down adds are sizing: one position, average = entry fill (with adds the exit would come sooner).
- The 2017 time filter is the author's backtest window. "Renko" is only in the description. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
