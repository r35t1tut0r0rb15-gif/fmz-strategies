# #458234 Multi Candlestick Pattern Recognition and Trading Strategy -> `fmz_458234_bullish_engulfing_no_exit_long`

- FMZ source id: 458234 (lineage).
- Source: https://www.fmz.com/strategy/458234 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:10:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C204). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Engulfing candles |
| 3 | PASS | Exchange pair in the header only (crude oil named in the title). |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (the default pattern).

## Ambiguities resolved

- Default pattern only; no exit (as written). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
