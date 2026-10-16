# #430748 Trend Following Strategy with Dynamic Stops -> `fmz_430748_ut_bot_atr_trail`

- FMZ source id: 430748 (lineage).
- Source: https://www.fmz.com/strategy/430748 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 13:46:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR trailing line. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND428704. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `atr_period` [10, 20]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
