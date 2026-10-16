# #427616 RSI Candlestick Trading Strategy -> `fmz_427616_rsi_candlestick_patterns`

- FMZ source id: 427616 (lineage).
- Source: https://www.fmz.com/strategy/427616 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-22 17:10:39). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and candle ratios only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `bull` [55, 60] x `bear` [45, 40]: **8 trials**; defaults 14 / 55 / 45 (the source's); the trend RSI(close) length 14 fixed.

## Ambiguities resolved

- Entries with qty 0 only close the opposite position (Noro's idiom).
- Drawn-only patterns (inverted hammer, engulfings, evening star) do not trade.
- Pattern formulas as written. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
