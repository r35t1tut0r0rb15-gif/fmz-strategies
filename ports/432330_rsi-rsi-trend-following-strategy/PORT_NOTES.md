# #432330 RSI趋势跟踪策略RSI-Trend-Following-Strategy -> `fmz_432330_rsi_rwma_roc_trail`

- FMZ source id: 432330 (lineage).
- Source: https://www.fmz.com/strategy/432330 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-16 15:33:40). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry; the trail is a house trail (approximation stated) |
| 2 | PASS | RSI levels, MA rate of change, ATR stop and percentage trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed-ratio order amounts and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG432330. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`activate` [0.12, 0.06] x `sl_atr` [3.0, 1.5]: **4 trials**; RSI 20, RWMA 20, the ROC thresholds, ATR 20 and the 3 % trail fixed.

## Ambiguities resolved

- Trail activation as a fixed gain (the source's is 4 ATR). Marks trailing_stop, coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop, coarse_bar_stop`
