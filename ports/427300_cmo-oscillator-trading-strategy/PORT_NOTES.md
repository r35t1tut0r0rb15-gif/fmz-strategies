# #427300 CMO Oscillator Trading Strategy -> `fmz_427300_cmo_abs_average`

- FMZ source id: 427300 (lineage).
- Source: https://www.fmz.com/strategy/427300 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-19 21:16:26). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Ratio of price changes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`top_band` [58, 40, 70] x `low_band` [5, 15]: **6 trials**; defaults 58 / 5 (the source's); lengths 5 / 10 / 20 fixed.

## Ambiguities resolved

- As written, a strong move either way buys and a quiet market sells (the absolute value).
- REVERSAL INTENDED. FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
