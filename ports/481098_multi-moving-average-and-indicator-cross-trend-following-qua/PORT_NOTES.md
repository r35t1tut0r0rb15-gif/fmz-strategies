# #481098 Multi Moving Average and Indicator Cross Trend Following Quantitative Trading System -> `fmz_481098_ema_stack_macd_rsi_volume_state_reversal`

- FMZ source id: 481098 (lineage).
- Source: https://www.fmz.com/strategy/481098 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-08 14:58:45). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked-EMA trend with MACD, RSI and volume confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_mult` [1.5, 1.0] x `rsi_mid` [50.0, 55.0]: **4 trials**; EMA 5 / 14 / 34 / 55, MACD 12 / 26 / 9.

## Ambiguities resolved

- Entries are states. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_agreement"`.

## Marks

`none`
