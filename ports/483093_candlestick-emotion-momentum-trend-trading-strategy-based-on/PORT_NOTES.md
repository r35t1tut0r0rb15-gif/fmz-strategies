# #483093 Candlestick Emotion Momentum Trend Trading Strategy Based on Quantitative Indicators -> `fmz_483093_candle_emotion_index_cooldown_time_loss_exits`

- FMZ source id: 483093 (lineage).
- Source: https://www.fmz.com/strategy/483093 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 13:23:51). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle-pattern sentiment crossings with volume, time and loss exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_hold` [20, 40] x `cooldown` [10, 5]: **4 trials**; lookback 14, levels 0.1 / 0.2, volume x 1.5.

## Ambiguities resolved

- Recursive var scores, as written. Volume = broker tick volume. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`none`
