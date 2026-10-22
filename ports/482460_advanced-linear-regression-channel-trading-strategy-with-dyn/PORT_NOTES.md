# #482460 Advanced Linear Regression Channel Trading Strategy with Dynamic Exit System -> `fmz_482460_linreg30_channel_touch_move_filter_body_exit_pct_bracket_reversal`

- FMZ source id: 482460 (lineage).
- Source: https://www.fmz.com/strategy/482460 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:18:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; lower-time-frame value from the bar's last block; avg-price bracket |
| 2 | PASS | Regression-channel touches with move filters and body-crossing exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [30, 60] x `mult` [2.0, 2.5]: **4 trials**; moves 1.8 % / 5 % / 0.2 %, bracket 10 % / 5 %.

## Ambiguities resolved

- The touch flags are never cleared, as written. The 3-minute close[1] is the block before the bar's last one.
- REVERSAL INTENDED. FREQ = "12h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`coarse_bar_stop`
