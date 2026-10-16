# #428616 TrumpBollingerEMAcandlestick Strategy -> `fmz_428616_day_direction_follower`

- FMZ source id: 428616 (lineage).
- Source: https://www.fmz.com/strategy/428616 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 15:30:27). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Percentage change only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dt` [0.0001, 0.005, 0.01, 0.02]: **4 trials**; default 0.0001 (the source's).

## Ambiguities resolved

- The 'D' securities are the daily chart itself; bands, Fibonacci levels, EMA signals and pivots are drawn only; the exits have no levels (inert).
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
