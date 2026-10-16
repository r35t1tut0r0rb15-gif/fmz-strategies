# #427347 Dual SMA Trend Following Strategy -> `fmz_427347_noro_trend_sma_v14`

- FMZ source id: 427347 (lineage).
- Source: https://www.fmz.com/strategy/427347 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-20 11:35:30). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.
- Related in idea (no near-duplicate group) to #427189 (Noro's Trend MAs v1.7, FMZ-C batch C2).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths, bar counts. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow_len` [20, 10, 40] x `bars` [2, 1]: **6 trials**; defaults 20 / 2 (the source's); fast EMA 5 filter on.

## Ambiguities resolved

- The "SMAs" are EMAs in the code; the channel is of ohlc4.
- REVERSAL INTENDED. FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
