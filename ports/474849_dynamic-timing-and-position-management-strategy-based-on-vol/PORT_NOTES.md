# #474849 Dynamic Timing and Position Management Strategy Based on Volatility -> `fmz_474849_volatility_stop_atr20x2_flip_reversal`

- FMZ source id: 474849 (lineage).
- Source: https://www.fmz.com/strategy/474849 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 15:19:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility-stop flips with stop-hit closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based size from a typed capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10] x `factor` [2.0, 3.0]: **4 trials**.

## Ambiguities resolved

- The clock close never fires on daily bars. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
