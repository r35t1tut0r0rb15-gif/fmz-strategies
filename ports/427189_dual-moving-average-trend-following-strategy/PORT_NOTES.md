# #427189 Dual Moving Average Trend Following Strategy -> `fmz_427189_noro_trend_mas_v17`

- FMZ source id: 427189 (lineage).
- Source: https://www.fmz.com/strategy/427189 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-18 21:57:00). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C2). Not run.
- Near-duplicate group: **ND427189** (with #440999, Jaccard 0.727); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths, bar counts. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity; the percent stop (off by default) stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427189. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40] x `ma_type` [7 mid-channel, 1 SMA, 2 EMA]: **9 trials**; defaults 20 / 7 (the source's); fast EMA 5 filter on, two-bar colour test fixed.

## Ambiguities resolved

- Stops off by default: no stop is placed (the level stays na).
- vwma (type 3) excluded: volume (rule 8 / check 8).
- trend is na until its first state; REVERSAL INTENDED. FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
