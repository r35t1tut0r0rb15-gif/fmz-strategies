# #440056 双K线预测闭合策略Dual-Candlestick-Prediction-Close-Strategy -> `fmz_440056_two_candle_30m_projection_daily`

- FMZ source id: 440056 (lineage).
- Source: https://www.fmz.com/strategy/440056 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 10:58:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; lower-time-frame values from the day's last bar |
| 2 | PASS | Candle colours and a projected close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ltf` ["30min", "60min"]: **2 trials**.

## Ambiguities resolved

- Lower-time-frame candles from the day's last bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
