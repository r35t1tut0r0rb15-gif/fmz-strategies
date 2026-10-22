# #442644 基于ATR和EMA的趋势跟随策略All-about-the-ATR-and-EMA-based-trend-following-strategy -> `fmz_442644_open_jump_atr_range_ema_filter_bracket`

- FMZ source id: 442644 (lineage).
- Source: https://www.fmz.com/strategy/442644 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-23 14:34:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The lot quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [37, 20] x `atr_mult` [0.2, 0.5]: **4 trials**; the ATR multiples of the bracket fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples at an interpolated 3-hour reading. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`coarse_bar_stop`
