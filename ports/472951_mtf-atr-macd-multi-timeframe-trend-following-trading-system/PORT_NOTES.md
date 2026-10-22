# #472951 MTF ATR MACD Multi Timeframe Trend Following Trading System with ATR and MACD Integration -> `fmz_472951_ema9_21_cross_rsi_ema_macd_confirm_reversal`

- FMZ source id: 472951 (lineage).
- Source: https://www.fmz.com/strategy/472951 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 14:42:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with RSI, EMA and MACD confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND472951. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; the RSI and MACD settings fixed.

## Ambiguities resolved

- Exits only on reversal bars (no effect, as written). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
