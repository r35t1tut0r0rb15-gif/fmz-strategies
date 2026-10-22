# #482846 Dual Moving Average Trend Trading Strategy with Stop Loss and Take Profit -> `fmz_482846_sma9_21_cross_1pct_bracket_long`

- FMZ source id: 482846 (lineage).
- Source: https://www.fmz.com/strategy/482846 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:36:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C251). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | SMA crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_percent` [1.0, 2.0] x `take_profit_percent` [1.0, 2.0]: **4 trials**; SMA 9 / 21.

## Ambiguities resolved

- The bracket sent with na levels on the signal bar is ported from the fill, active from the fill bar.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
