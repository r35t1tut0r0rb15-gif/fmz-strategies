# #440878 基于多时间框架的一云延伸MACD和DMI组合策略Multi-Timeframe-Ichimoku-MACD-and-DMI-Combined-Strategy -> `fmz_440878_three_tf_ichimoku_macd_dmi`

- FMZ source id: 440878 (lineage).
- Source: https://www.fmz.com/strategy/440878 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 18:04:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 15-minute values end with the chart bar, 4-hour values from completed bars |
| 2 | PASS | Ichimoku span, MACD and DMI on three timeframes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [25, 20] x `length_dmi` [14, 7]: **4 trials**; Ichimoku and MACD settings fixed.

## Ambiguities resolved

- 15-minute values from the last 15-minute bar; 4-hour values from the last completed bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
