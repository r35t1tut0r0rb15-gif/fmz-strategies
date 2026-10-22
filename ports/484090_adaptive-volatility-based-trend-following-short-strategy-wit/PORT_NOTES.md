# #484090 Adaptive Volatility Based Trend Following Short Strategy with Time Delay and Stop Loss Protection -> `fmz_484090_close_under_sma50_below_sma200_atr_range_filter_delayed_exit_short`

- FMZ source id: 484090 (lineage).
- Source: https://www.fmz.com/strategy/484090 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 09:42:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C260). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; high-based percent stop as an exit signal |
| 2 | PASS | SMA crossings with volatility and range filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma_length` [50, 20] x `stop_loss_percent` [0.5, 1.0]: **4 trials**; SMA 200, ATR 14 / 28, range 20 bars 0.03 %, delay 10 minutes.

## Ambiguities resolved

- The exits are tested only while the filters hold, as written. Short only. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
