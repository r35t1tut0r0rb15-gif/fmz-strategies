# #473366 Multi Dimensional Technical Indicator Trend Following Quantitative Strategy -> `fmz_473366_rsi_macd_ema_any_of_three_bias_reversal`

- FMZ source id: 473366 (lineage).
- Source: https://www.fmz.com/strategy/473366 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:33:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Any-of-three indicator bias; profit-armed stop described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital and risk inputs shown only. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and levels are constants; the three switches on; the stop is pending).

## Ambiguities resolved

- The short wins a bar with both entries (call order). Profit-armed per-bar stop pending. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
