# #482477 Multi Period EMA Trend Following with Support Resistance Hybrid Trading System -> `fmz_482477_hh9_break_or_ema20_50_atr_trend_reversal`

- FMZ source id: 482477 (lineage).
- Source: https://www.fmz.com/strategy/482477 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:52:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar ATR stop described (pending) |
| 2 | PASS | Range breakouts or EMA trend state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sup_res_lookback` [9, 20] x `atr_period` [14, 28]: **4 trials**; EMA 20 / 50; the 10 ATR stop is pending.

## Ambiguities resolved

- The per-bar 10 ATR stop is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`trailing_stop_pending`
