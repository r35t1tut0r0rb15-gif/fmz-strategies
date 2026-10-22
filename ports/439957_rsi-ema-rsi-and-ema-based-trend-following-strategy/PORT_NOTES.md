# #439957 基于RSI和EMA的趋势跟踪策略RSI-and-EMA-Based-Trend-Following-Strategy -> `fmz_439957_rsi_dip_any_ema_side_long`

- FMZ source id: 439957 (lineage).
- Source: https://www.fmz.com/strategy/439957 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-25 12:19:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C127). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and EMA sides |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed size and the unused risk inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `oversold` [30, 20]: **4 trials**; overbought 70 and the EMAs fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
