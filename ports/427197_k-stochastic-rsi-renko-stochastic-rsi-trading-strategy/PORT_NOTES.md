# #427197 Renko Stochastic RSI Trading Strategy -> `fmz_427197_stoch_rsi_cross`

- FMZ source id: 427197 (lineage).
- Source: https://www.fmz.com/strategy/427197 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-18 22:33:09). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator crosses. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commission setting stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [20, 14] x `stoch_length` [3, 14] x `smooth_k` [5, 3]: **8 trials**; defaults 20 / 3 / 5 (the source's); D 2 fixed.

## Ambiguities resolved

- "Renko" appears only in the description; the code and the FMZ backtest use 3-hour time bars.
- Always in the market after the first cross (REVERSAL INTENDED). FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
