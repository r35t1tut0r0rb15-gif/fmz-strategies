# #441044 Willy Wonka Breakout Strategy -> `fmz_441044_rsi_28_72_level_reversal`

- FMZ source id: 441044 (lineage).
- Source: https://www.fmz.com/strategy/441044 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 10:00:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 9] x `oversold` [28, 20]: **4 trials**; overbought = 100 - oversold.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
