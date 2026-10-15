# #427090 Dual Moving Average Crossover Strategy -> `fmz_427090_noro_ma_trend_flip`

- FMZ source id: 427090 (lineage).
- Source: https://www.fmz.com/strategy/427090 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-17 22:35:07). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.
- Near-duplicate group: **ND427090** (with #436514, Jaccard 0.789); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per trade stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427090. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30, 50] x `ma_type` [1 SMA, 2 EMA, 6 KAMA]: **9 trials**; defaults 30 / 1 (the source's). Types 4, 5, 7 are implemented but not in the grid; type 3 (vwma, volume) is not ported.

## Ambiguities resolved

- vwma uses volume: excluded (rule 8 / check 8).
- KAMA starts from 0 as written (`nz(kama[1])`).
- A flip needs a defined previous trend state; always in the market after the first flip (REVERSAL INTENDED).
- FREQ = "10min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
