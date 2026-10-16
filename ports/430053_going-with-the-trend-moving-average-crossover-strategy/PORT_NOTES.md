# #430053 Going with the Trend Moving Average Crossover Strategy -> `fmz_430053_sma_cross_rsi_atr_bracket`

- FMZ source id: 430053 (lineage).
- Source: https://www.fmz.com/strategy/430053 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-24 16:14:10). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (the shared-id re-binding approximated). |
| 2 | PASS | Moving averages, an RSI level and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430053. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `atr_mult` [2.0, 3.0]: **4 trials**; SMA 30, RSI 14 / 50 and ATR 14 fixed.

## Ambiguities resolved

- Bracket levels from the signal bar, re-based on the fill; the shared exit id's re-binding to the other side is not
  modelled (approximation).
- Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
