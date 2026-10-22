# #440314 基于ADXMA和EMA的只做多趋势跟踪策略ADX-MA-and-EMA-Long-Only-Trend-Tracking-Strategy -> `fmz_440314_rising_adx_above_ma_ema_long`

- FMZ source id: 440314 (lineage).
- Source: https://www.fmz.com/strategy/440314 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 11:30:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ADX slope and averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_period` [50, 20] x `adx_len` [14, 7]: **4 trials**; the EMA period follows the MA period; DI length 14 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
