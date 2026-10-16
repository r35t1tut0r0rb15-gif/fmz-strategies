# #427507 Volatility Range Breakout Trading Strategy -> `fmz_427507_volatility_range_breakout`

- FMZ source id: 427507 (lineage).
- Source: https://www.fmz.com/strategy/427507 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-21 20:38:29). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bands as fractions of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 20 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`avg_length` [100, 50] x `vol_length` [100, 50] x `exit_type` [1 Volatility MA, 2 Range Crossover]: **8 trials**; defaults 100 / 100 / 1 (the source's).

## Ambiguities resolved

- The script's `wma(x, n, w)` uses one weight for every term: it equals the simple average (ported so).
- Adds (pyramiding 20) are sizing. Entries win over same-bar closes (REVERSAL INTENDED). FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
