# #454137 Chande-Kroll止损动态ATR趋势跟踪策略-Chande-Kroll-Stop-Dynamic-ATR-Trend-Following-Strategy -> `fmz_454137_chande_kroll_low_stop_cross_long`

- FMZ source id: 454137 (lineage).
- Source: https://www.fmz.com/strategy/454137 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-14 15:15:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C193). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Chande Kroll stop-line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-formula quantity, commission and slippage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_len` [21, 10] x `atr_mult` [3.0, 2.0] x `sma_len` [21, 50]: **8 trials**; the ATR 10 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
