# #427445 Simple Moving Average Crossover Strategy -> `fmz_427445_three_sma_delay_as_written`

- FMZ source id: 427445 (lineage).
- Source: https://www.fmz.com/strategy/427445 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 10:47:24). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
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

`bars_wait` [5, 2, 10] x `sma_low` [200, 100]: **6 trials**; defaults 5 / 200 (the source's); SMA 20 / 50 fixed; the wait is the same for both sides (both inputs default 5).

## Ambiguities resolved

- **As written**, the long is closed by the source's `close_short` (a LONG alignment without a short alignment 6 bars back), and the short by `close_long`: longs last about one bar after their fill. **Decision owed:** port the evidently intended version (closes swapped) as a separate module.
- REVERSAL INTENDED. FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
