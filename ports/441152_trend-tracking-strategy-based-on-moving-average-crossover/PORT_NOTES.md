# #441152 Trend Tracking Strategy Based on Moving Average Crossover -> `fmz_441152_ema_cross_strong_smoothed_rsi_long`

- FMZ source id: 441152 (lineage).
- Source: https://www.fmz.com/strategy/441152 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-06 11:37:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C147). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings, smoothed RSI and close-vs-fill tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG441152. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_entry` [65, 55] x `rsi_exit` [40, 30]: **4 trials**; EMAs and the price tests fixed.

## Ambiguities resolved

- Close-vs-fill price exits. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
