# #452824 EMA趋势动量K线形态策略-EMA-Trend-Momentum-Candlestick-Pattern-Strategy -> `fmz_452824_bullish_engulfing_ema50_ao_2pct_stop_long`

- FMZ source id: 452824 (lineage).
- Source: https://www.fmz.com/strategy/452824 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-29 17:11:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop as a fixed fraction; re-issued stops pending (mark) |
| 2 | PASS | Engulfing bars in an EMA uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 100] x `sl_pct` [0.02, 0.05]: **4 trials**; the AO lengths fixed.

## Ambiguities resolved

- Re-issued stops pending; the stop is the only exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
