# #483044 Dynamic Multi Indicator Optimized Trend Following Strategy -> `fmz_483044_ichimoku_side_macd_weekly_sma50_bbwidth_atr_stop_reversal`

- FMZ source id: 483044 (lineage).
- Source: https://www.fmz.com/strategy/483044 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:46:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop as a fraction of the fill |
| 2 | ADAPT | The -0.05 histogram level read as a fraction of the close at the header's prices |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [1.5, 2.5] x `bb_width_threshold` [0.02, 0.05]: **4 trials**; ATR 14, weekly SMA 50, histogram level -1.667e-05 x close.

## Ambiguities resolved

- The -0.05 histogram level is read at ETH prices. The weekly value is the last week completed by the bar's last day.
- Repeat state signals re-send the stop; pending. MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
