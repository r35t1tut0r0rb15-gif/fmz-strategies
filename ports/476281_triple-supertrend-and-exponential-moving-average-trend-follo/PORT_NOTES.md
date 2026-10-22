# #476281 Triple Supertrend and Exponential Moving Average Trend Following Quantitative Trading Strategy -> `fmz_476281_triple_supertrend_ema50_reversal`

- FMZ source id: 476281 (lineage).
- Source: https://www.fmz.com/strategy/476281 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 15:56:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Triple SuperTrend agreement with an EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [50, 200] x `atr_period` [10, 20]: **4 trials**; factors 3 / 2 / 1.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
