# #427526 Momentum Moving Average Crossover Strategy -> `fmz_427526_tale_indicators_as_written`

- FMZ source id: 427526 (lineage).
- Source: https://www.fmz.com/strategy/427526 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 21:29:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths, a price ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | qty 4 / 1, capital, commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_fast` [3, 5] x `len_slow` [15, 30] x `exit_tuner` [0.005, 0.01]: **8 trials**; defaults 3 / 15 / 0.005 (the source's); exit EMA 3 fixed.

## Ambiguities resolved

- **As written**, including three slips (short-exit cross on the high EMA, `bull_exit[2]` in bear_r, bear_reenter setting the long flag), and the orders reading the flags after this bar's updates (most closes pre-empted). **Decision owed:** a cleaned-up version as a separate module.
- Entries win over same-bar closes (REVERSAL INTENDED). Broker-day bars. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
