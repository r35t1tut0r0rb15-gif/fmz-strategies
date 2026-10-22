# #482837 Multi Timeframe Stochastic Oscillator Swing Trading Strategy with Dynamic Take Profit and Stop Loss -> `fmz_482837_stoch14_kd_cross_last_30min_confirm_1_7pct_bracket_reversal`

- FMZ source id: 482837 (lineage).
- Source: https://www.fmz.com/strategy/482837 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:49:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C251). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | Stochastic crossings with a 30-minute confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_length` [14, 9] x `tp_sl_pct` [1.7, 3.0]: **4 trials**; smooth 3, D 3, 30-minute confirmation.

## Ambiguities resolved

- The lower-time-frame security without lookahead is the day's last 30-minute block.
- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
