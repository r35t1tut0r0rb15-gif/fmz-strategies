# #432782 Quantitative Trading Strategy Based on Daily Close Price Comparison -> `fmz_432782_daily_close_comparison`

- FMZ source id: 432782 (lineage).
- Source: https://www.fmz.com/strategy/432782 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-21 14:34:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the previous completed day |
| 2 | PASS | The sign of the daily change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427066. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`threshold` [0.0, 0.004, 0.008]: **3 trials** (the input's own step).

## Ambiguities resolved

- Previous day's close from [1], no look-ahead. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
