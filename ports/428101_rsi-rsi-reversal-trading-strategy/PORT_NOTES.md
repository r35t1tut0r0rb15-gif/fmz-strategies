# #428101 RSI Reversal Trading Strategy -> `fmz_428101_rsi_open_reversal_extras`

- FMZ source id: 428101 (lineage).
- Source: https://www.fmz.com/strategy/428101 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 16:09:39). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17) AS WRITTEN. Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Price-unit offset n -> fraction of the entry price (default 0). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin / leverage and the off exits stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `over_sold` [44, 30]: **4 trials**; defaults 14 / 44 (the source's); overbought 67 and `n_frac` 0 fixed.

## Ambiguities resolved

- RSI of the open. n is not var (0.0577 plus 1000 after a signal on that bar, as written).
- The short extras test close < avg price like the longs (as written). Exits off. REVERSAL INTENDED.
- Average price = the fill (next open); one trade at most. Broker-day bars; FREQ = "1D".

## Decision owed

The intended direction of the short extras' price test and whether n was meant in pips.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
