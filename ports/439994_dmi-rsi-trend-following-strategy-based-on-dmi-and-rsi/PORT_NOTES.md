# #439994 基于DMI和RSI的趋势跟随策略Trend-Following-Strategy-Based-on-DMI-and-RSI -> `fmz_439994_dmi_rsi_counter_extremes_stop`

- FMZ source id: 439994 (lineage).
- Source: https://www.fmz.com/strategy/439994 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 15:56:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent stop from the fill |
| 2 | PASS | RSI extremes and DMI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the stop factor stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_factor` [0.5, 1.0] x `rsi_length` [14, 7]: **4 trials**; ADX 20 and DI 14 fixed.

## Ambiguities resolved

- Fixed percent stop from the fill. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
