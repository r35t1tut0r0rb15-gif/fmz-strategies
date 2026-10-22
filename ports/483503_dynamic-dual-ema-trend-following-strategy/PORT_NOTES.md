# #483503 Dynamic Dual EMA Trend Following Strategy -> `fmz_483503_ema44_high_low_break_ema200_side_reversal`

- FMZ source id: 483503 (lineage).
- Source: https://www.fmz.com/strategy/483503 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:50:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving EMA stops pending |
| 2 | PASS | EMA-of-extremes breakouts with an EMA 200 filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [44, 20] x `long_term_length` [200, 100]: **4 trials**.

## Ambiguities resolved

- The per-bar EMA stops are pending, not ported. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`trailing_stop_pending`
