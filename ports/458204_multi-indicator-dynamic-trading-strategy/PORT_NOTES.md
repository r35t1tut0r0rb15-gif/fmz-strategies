# #458204 Multi Indicator Dynamic Trading Strategy -> `fmz_458204_ema34_89_cross_rsi_volume_15bar_ema_stop_1h_reversal`

- FMZ source id: 458204 (lineage).
- Source: https://www.fmz.com/strategy/458204 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 17:29:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; EMA 34 stop followed in the signals |
| 2 | PASS | EMA 34 / 89 crossings with RSI filter, volume and time exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold` [15, 30] x `vol_mult` [3.0, 2.0]: **4 trials**; EMA 34 / 89, RSI 14, volume SMA 20.

## Ambiguities resolved

- EMA 34 stop followed at the next open after the touch. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
