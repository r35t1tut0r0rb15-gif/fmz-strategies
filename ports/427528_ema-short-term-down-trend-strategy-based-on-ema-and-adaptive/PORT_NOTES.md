# #427528 Short-term Down Trend Strategy Based on EMA and Adaptive Fibonacci Retracement -> `fmz_427528_cc_trend_short`

- FMZ source id: 427528 (lineage).
- Source: https://www.fmz.com/strategy/427528 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-21 21:36:16). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths, retracement fractions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fib_len` [100, 50, 200] x `retrace` [0.236, 0.382]: **6 trials**; defaults 100 / 0.236 (the source's); EMAs 9 / 21 / 55 / 200 fixed.

## Ambiguities resolved

- `openprofit >= 0` read as the close at or below the short's fill price (sizing-free).
- Short only. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
