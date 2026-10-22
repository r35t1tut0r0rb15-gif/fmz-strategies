# #476259 Dynamic Moving Average and Bollinger Bands Cross Strategy with Fixed Stop Loss Optimization Model -> `fmz_476259_bb20_reentry_sma200_side_band_close_avg_stop_reversal`

- FMZ source id: 476259 (lineage).
- Source: https://www.fmz.com/strategy/476259 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 14:57:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the stop base, as written |
| 2 | PASS | Bollinger re-entries on the SMA 200 side with band closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `ma_length` [200, 100]: **4 trials**; 2 sd, stop 3 %.

## Ambiguities resolved

- The stop exists only on a reversal (from the replaced position's price), as written; repeat-signal stops not followed.
- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
