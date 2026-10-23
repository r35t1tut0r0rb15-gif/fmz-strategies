# #449721 Multi Indicator Trend Following Strategy -> `fmz_449721_sma9_21_cross_macd_volume_atr_tick_bracket_1h_reversal`

- FMZ source id: 449721 (lineage).
- Source: https://www.fmz.com/strategy/449721 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-28 14:25:12). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR-tick bracket from the signal bar as fractions of the fill |
| 2 | PASS | SMA crossings confirmed by MACD and volume |
| 3 | PASS | Exchange pair in the header only; tick counts converted at the source's 0.1 tick. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_k` [0.2, 1.0] x `tp_k` [0.4, 2.0]: **4 trials**; SMA 9 / 21, MACD 12 / 26 / 9, ATR 14.

## Ambiguities resolved

- ATR used as a tick count, converted at the 0.1 tick (0.2 / 0.4 ATR). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
