# #483034 Zero Lag Trend Momentum Indicator Trading Strategy -> `fmz_483034_zero_lag_ema50_score_atr_band_reversal`

- FMZ source id: 483034 (lineage).
- Source: https://www.fmz.com/strategy/483034 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:19:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent close exits pending |
| 2 | PASS | Zero-lag trend score with an ATR band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 30] x `volatility_mult` [1.5, 1.0]: **4 trials**; score loop 1-50, thresholds 5 / -5.

## Ambiguities resolved

- The exits re-sent each bar from the close are pending, not ported. MPL 2.0 source, ported and stated.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`trailing_stop_pending`
