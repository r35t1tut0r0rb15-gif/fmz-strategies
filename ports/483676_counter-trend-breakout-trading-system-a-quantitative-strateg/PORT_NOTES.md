# #483676 Counter Trend Breakout Trading System A Quantitative Strategy Based on Multi Day Price Patterns and Volatility Filtering -> `fmz_483676_three_red_days_atr_filter_three_green_or_22_bar_exit_long`

- FMZ source id: 483676 (lineage).
- Source: https://www.fmz.com/strategy/483676 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-25 10:49:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C260). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Red-day runs with a volatility filter and a bar-count exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_trade_duration` [22, 10] x `atr_period` [12, 20]: **4 trials**; ATR average 30, green exit on.

## Ambiguities resolved

- The entryBarIndex reset on a close-fill bar is followed as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
