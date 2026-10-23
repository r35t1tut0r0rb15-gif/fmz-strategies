# #453669 趋势过滤Pin-Bar反转策略-Trend-Filtered-Pin-Bar-Reversal-Strategy -> `fmz_453669_trend_filtered_pin_bar_body_bracket_1h_reversal`

- FMZ source id: 453669 (lineage).
- Source: https://www.fmz.com/strategy/453669 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 16:48:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; body-based bracket fixed at the signal bar as fractions of the fill |
| 2 | PASS | Trend-filtered pin bars on above-average volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wick` [0.6, 0.5] x `sma_len` [50, 100]: **4 trials**; body 0.3, SL 2 bodies, TP 3 bodies.

## Ambiguities resolved

- Re-sent bracket fixed at the signal bar. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
