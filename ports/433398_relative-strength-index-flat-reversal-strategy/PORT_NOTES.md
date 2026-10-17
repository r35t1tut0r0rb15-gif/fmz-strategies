# #433398 Relative Strength Index Flat Reversal Strategy -> `fmz_433398_rsi_30_70_cross`

- FMZ source id: 433398 (lineage).
- Source: https://www.fmz.com/strategy/433398 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-27 11:25:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

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

`length` [14, 7] x `levels` [30, 20]: **4 trials**; the short level is 100 - levels (70 as written).

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
