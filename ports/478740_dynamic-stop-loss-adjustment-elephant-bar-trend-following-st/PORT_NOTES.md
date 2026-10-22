# #478740 Dynamic Stop Loss Adjustment Elephant Bar Trend Following Strategy -> `fmz_478740_elephant_bar_body18_candle_bracket_reversal`

- FMZ source id: 478740 (lineage).
- Source: https://www.fmz.com/strategy/478740 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 16:24:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Elephant-bar momentum entries with a candle-based bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`size_mult` [1.8, 2.5] x `profit_mult` [1.8, 3.0]: **4 trials**; average 15 bars, close within 10 %.

## Ambiguities resolved

- Dynamic stop steps reach the orders only through repeat signals, which are not followed. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
