# #485291 Multi Dimensional Technical Indicator Cross Confirmation Buy Signal Optimization Strategy -> `fmz_485291_nine_condition_vote_buy_no_exit_long_only`

- FMZ source id: 485291 (lineage).
- Source: https://www.fmz.com/strategy/485291 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-07 14:31:03). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A nine-condition bullish vote |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`min_conditions` [2, 4] x `fib_len` [260, 120]: **4 trials**.

## Ambiguities resolved

- No exit: one long held to the end of the data. Stochastic arguments shifted, as written. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "indicator_vote"`.

## Marks

`none`
