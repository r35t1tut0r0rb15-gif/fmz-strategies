# #488128 Multi Indicator Trend Confirmation High Profit Quantitative Trading Strategy -> `fmz_488128_ema_macd_cross_trend_stack_volume_rolling_stop_1h_long_only`

- FMZ source id: 488128 (lineage).
- Source: https://www.fmz.com/strategy/488128 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 11:36:57). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar re-sent stop followed in the signals |
| 2 | PASS | Aligned EMA and MACD crossings in a strong uptrend on volume |
| 3 | PASS | Exchange pair in the header only (Solana named in the title). |
| 4 | DONE | 30 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.02, 0.03] x `tp` [1.0, 0.1]: **4 trials**; EMA 10 / 20 / 50 / 100 / 200, RSI 14, volume x 1.5.

## Ambiguities resolved

- Rolling 2 % stop followed at the next open. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_agreement"`.

## Marks

`trailing_stop_pending`
