# #477609 Dual Technical Indicator Momentum Reversal Trading Strategy with Risk Management System -> `fmz_477609_rsi14_bb20_extreme_swing5_stop_2r_reversal`

- FMZ source id: 477609 (lineage).
- Source: https://www.fmz.com/strategy/477609 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:45:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar swing bracket as fractions of the fill |
| 2 | PASS | RSI / Bollinger extremes with a swing stop and 2 R target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the R:R input unused. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing` [5, 10] x `rr` [2.0, 1.0]: **4 trials**; RSI 14 / 30 / 70, BB 20 / 2.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
