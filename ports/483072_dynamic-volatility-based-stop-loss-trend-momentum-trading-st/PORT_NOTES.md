# #483072 Dynamic Volatility Based Stop Loss Trend Momentum Trading Strategy -> `fmz_483072_macd_cross_over_ema20_long`

- FMZ source id: 483072 (lineage).
- Source: https://www.fmz.com/strategy/483072 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:39:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C256). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ratchet stop pending |
| 2 | PASS | MACD crossings over an EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`macd_fast_length` [12, 8] x `ema_length` [20, 50]: **4 trials**; MACD slow 26, signal 9.

## Ambiguities resolved

- The ratchet stop on close - 2 ATR is pending (not the house volatility trail). Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`
