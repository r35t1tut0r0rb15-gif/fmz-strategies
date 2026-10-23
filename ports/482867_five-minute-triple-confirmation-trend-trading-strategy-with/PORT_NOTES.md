# #482867 Five Minute Triple Confirmation Trend Trading Strategy with Risk Management System -> `fmz_482867_triple_confirmation_ema_macd_volume_obv_rolling_bracket_1m_reversal`

- FMZ source id: 482867 (lineage).
- Source: https://www.fmz.com/strategy/482867 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:53:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar re-sent bracket followed in the signals |
| 2 | PASS | Same-bar EMA and MACD crossings with RSI, volume and OBV confirmation |
| 3 | PASS | Exchange pair in the header only (SOL_USDT). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 2.5] x `rr` [2.0, 1.5]: **4 trials**; EMA 9 / 21, RSI 14, MACD 12 / 26 / 9, volume x 1.8.

## Ambiguities resolved

- Re-sent bracket followed at the next open. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_agreement"`.

## Marks

`trailing_stop_pending`
