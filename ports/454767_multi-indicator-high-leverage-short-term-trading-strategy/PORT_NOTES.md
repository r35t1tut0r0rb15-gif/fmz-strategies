# #454767 Multi Indicator High Leverage Short Term Trading Strategy -> `fmz_454767_ema5_15_cross_rsi_macd_atr_bracket_reversal`

- FMZ source id: 454767 (lineage).
- Source: https://www.fmz.com/strategy/454767 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 18:16:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ATR bracket as fractions of the signal close; re-issued levels pending (mark) |
| 2 | PASS | Confirmed EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [5, 9] x `long_len` [15, 21] x `atr_mult` [1.5, 3.0]: **8 trials**; the RSI and MACD settings fixed.

## Ambiguities resolved

- Re-issued levels pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
