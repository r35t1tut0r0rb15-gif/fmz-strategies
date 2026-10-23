# #482875 Volume Spike and RSI Enhanced Trading Strategy -> `fmz_482875_rsi_extreme_candle_volume_spike_atr_rr2_1h_reversal`

- FMZ source id: 482875 (lineage).
- Source: https://www.fmz.com/strategy/482875 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 16:08:21). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; candle-ATR bracket at the signal bar as fractions of the fill |
| 2 | PASS | RSI extremes with reversal candles on volume spikes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [2.0, 1.5] x `vol_mult` [1.5, 2.0]: **4 trials**; RSI 14 30 / 70, ATR 14.

## Ambiguities resolved

- Repeats re-send the bracket (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_reversion"`.

## Marks

`trailing_stop_pending`
