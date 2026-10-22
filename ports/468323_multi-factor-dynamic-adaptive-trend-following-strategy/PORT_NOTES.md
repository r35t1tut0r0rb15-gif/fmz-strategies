# #468323 Multi Factor Dynamic Adaptive Trend Following Strategy -> `fmz_468323_macd_rsi_sma50_200_agreement_atr_bracket_reversal`

- FMZ source id: 468323 (lineage).
- Source: https://www.fmz.com/strategy/468323 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 15:40:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR levels from the fill |
| 2 | PASS | MACD, RSI and SMA-stack agreement with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [2.0, 1.0] x `tp_atr` [3.0, 6.0]: **4 trials**; the indicator lengths fixed.

## Ambiguities resolved

- ATR of the bar before the fill; per-bar ATR movement pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
