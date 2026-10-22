# #439760 Multi Indicator Trend Reversal Trading Strategy -> `fmz_439760_gt51_harsi_ssl_coral_flips`

- FMZ source id: 439760 (lineage).
- Source: https://www.fmz.com/strategy/439760 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-23 15:33:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C124). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI candles, SSL channel and Coral trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`harsi_back` [6, 3] x `coral_back` [4, 2]: **4 trials**; SSL lookback 1 and the indicator settings fixed.

## Ambiguities resolved

- Default three-option branch only; alternating sides. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
