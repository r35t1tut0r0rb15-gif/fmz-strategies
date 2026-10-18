# #435835 Trend Tracking Strategy Based on Multi factor Model with Adaptive Trailing Stoploss -> `fmz_435835_ut_bot_atr_line_flips`

- FMZ source id: 435835 (lineage).
- Source: https://www.fmz.com/strategy/435835 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-19 11:04:27). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND435835. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`a` [10, 5] x `c` [10, 20]: **4 trials**.

## Ambiguities resolved

- ATR trailing line as a signal line. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
