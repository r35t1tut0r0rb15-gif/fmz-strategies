# #441965 Momentum Average Inverse Relief Pullback Strategy -> `fmz_441965_engulfing_ema50_cross_reversal`

- FMZ source id: 441965 (lineage).
- Source: https://www.fmz.com/strategy/441965 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-18 10:21:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Engulfing candles and EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [50, 100]: **2 trials**.

## Ambiguities resolved

- The "Exit" close never acts. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
