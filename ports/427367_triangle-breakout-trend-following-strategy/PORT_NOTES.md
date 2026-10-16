# #427367 Triangle Breakout Trend Following Strategy -> `fmz_427367_triangle_point_long`

- FMZ source id: 427367 (lineage).
- Source: https://www.fmz.com/strategy/427367 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 14:24:16). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 5 % stop is a close test. |
| 2 | PASS | Bar counts, stop as a fraction of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 2 / fixed qty 3 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`num_periods` [9, 5] x `slow_ema` [65, 30] x `stop_pct` [5, 2.5]: **8 trials**; defaults 9 / 65 / 5 (the source's); EMA 13 and 200 fixed.

## Ambiguities resolved

- The add below the average price is sizing; one position, average = entry fill.
- takeProfitVal is never used by an order. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
