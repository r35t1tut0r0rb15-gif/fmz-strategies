# #440086 渐进BB-KC趋势策略Gradual-BB-KC-Trend-Strategy -> `fmz_440086_keltner_bollinger_band_cross_volume_20bar_exit_1h_reversal`

- FMZ source id: 440086 (lineage).
- Source: https://www.fmz.com/strategy/440086 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 15:10:41). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-count exit |
| 2 | PASS | Keltner / Bollinger band crossings on above-average volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kc_mult` [2.2, 1.5] x `bars_in_trade` [20, 40]: **4 trials**; BB 20 x 2, volume SMA 10.

## Ambiguities resolved

- Bar counter as written (restarts on every signal); the stop / trail exits never act. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_channel"`.

## Marks

`none`
