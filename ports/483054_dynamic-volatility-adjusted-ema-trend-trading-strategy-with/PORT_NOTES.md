# #483054 Dynamic Volatility Adjusted EMA Trend Trading Strategy with Smart Stop Loss System -> `fmz_483054_ema9_21_cross_rsi_atr1_5_filter_close_stop1pct_reversal`

- FMZ source id: 483054 (lineage).
- Source: https://www.fmz.com/strategy/483054 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 11:11:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based percent stop |
| 2 | PASS | EMA crossings with RSI and an ATR distance filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [1.5, 1.0] x `stop_loss_percent` [1.0, 0.5]: **4 trials**; EMA 9 / 21 and RSI 14 fixed on 1-minute bars, ATR 14.

## Ambiguities resolved

- The lengths forced by the 1-minute branch are fixed. MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
