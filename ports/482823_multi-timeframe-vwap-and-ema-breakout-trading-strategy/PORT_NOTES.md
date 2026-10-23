# #482823 Multi Timeframe VWAP and EMA Breakout Trading Strategy -> `fmz_482823_ema_vwap_stack_candle_swing_atr_rr2_2h_reversal`

- FMZ source id: 482823 (lineage).
- Source: https://www.fmz.com/strategy/482823 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 13:25:02). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing-ATR bracket at the signal bar as fractions of the fill |
| 2 | PASS | Aligned EMA / VWAP trend candles |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [2.0, 3.0] x `swing` [10, 20]: **4 trials**; EMA 10 / 20 / 200, ATR 14.

## Ambiguities resolved

- The 1 : 2 target decides; repeats re-send the levels (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
