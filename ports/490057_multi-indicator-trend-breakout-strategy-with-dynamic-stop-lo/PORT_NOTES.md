# #490057 Multi Indicator Trend Breakout Strategy with Dynamic Stop Loss -> `fmz_490057_donchian20_10_ema50_rsi_atr_filter_atr_stop_reversal`

- FMZ source id: 490057 (lineage).
- Source: https://www.fmz.com/strategy/490057 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-11 11:01:00). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop at the signal close as a fraction of the fill |
| 2 | PASS | Donchian breakouts in the EMA trend with a volatility filter and channel exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and commission 0.045 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_len` [20, 55] x `atr_mult` [1.5, 2.5]: **4 trials**; exit channel 10, EMA 50, RSI 14, ATR 14 / SMA 20.

## Ambiguities resolved

- Repeats re-send the stop (pending); start date dropped. Volume not used (filter off). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
