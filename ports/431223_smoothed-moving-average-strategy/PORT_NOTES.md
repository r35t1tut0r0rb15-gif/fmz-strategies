# #431223 Smoothed Moving Average Strategy -> `fmz_431223_double_ema_turns`

- FMZ source id: 431223 (lineage).
- Source: https://www.fmz.com/strategy/431223 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 10:29:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A smoothed moving average's turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND431223. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [60, 30] x `loops` [2, 1]: **4 trials**; MA type EMA fixed.

## Ambiguities resolved

- EMA type only (the default). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
