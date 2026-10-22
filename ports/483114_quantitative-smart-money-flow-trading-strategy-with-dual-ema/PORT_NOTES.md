# #483114 Quantitative Smart Money Flow Trading Strategy with Dual EMA and Dynamic Order Block Detection -> `fmz_483114_order_block5_ema50_200_trend_swing_2r_reversal`

- FMZ source id: 483114 (lineage).
- Source: https://www.fmz.com/strategy/483114 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:10:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing bracket as fractions of the fill |
| 2 | PASS | Order-block bars with an EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [50, 20] x `risk_reward` [2.0, 3.0]: **4 trials**; EMA 200, swing 5 bars.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`trailing_stop_pending`
