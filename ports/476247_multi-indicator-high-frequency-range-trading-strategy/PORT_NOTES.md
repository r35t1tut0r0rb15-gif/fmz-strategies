# #476247 Multi Indicator High Frequency Range Trading Strategy -> `fmz_476247_ema8_21_cross_rsi_volume_nbar_1_5_0_7pct_bracket_reversal`

- FMZ source id: 476247 (lineage).
- Source: https://www.fmz.com/strategy/476247 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 14:18:57). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket at the signal close as fractions of the fill |
| 2 | PASS | EMA crossings with RSI, volume and higher-low filters |
| 3 | PASS | Exchange pair in the header only (XRP/USD named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.015, 0.03] x `sl` [0.007, 0.015]: **4 trials**; EMA 8 / 21, RSI 14, volume SMA 20, n-bars 5.

## Ambiguities resolved

- Bracket at the signal close. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
