# #430244 Multi Factor Strategy Combination -> `fmz_430244_stoch_rsi_double`

- FMZ source id: 430244 (lineage).
- Source: https://www.fmz.com/strategy/430244 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-26 15:18:34). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_stoch` [14, 7] x `rsi_len` [14, 7]: **4 trials**; smoothing 3 / 3 and levels 80 / 20, 70 / 30 fixed.

## Ambiguities resolved

- ds from the stochastic RSI, as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
