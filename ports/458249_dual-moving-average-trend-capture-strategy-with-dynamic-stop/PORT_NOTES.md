# #458249 Dual Moving Average Trend Capture Strategy with Dynamic Stop Loss and Filter -> `fmz_458249_close_sma14_cross_sma50_filter_prev_bar_stop_from_flat`

- FMZ source id: 458249 (lineage).
- Source: https://www.fmz.com/strategy/458249 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:46:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C204). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar levels as fractions of the fill |
| 2 | PASS | SMA crossings with a filter, previous-bar stop and percent target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [14, 30] x `filter_len` [50, 100] x `tp_pct` [0.01, 0.02]: **8 trials**; the MA types SMA fixed.

## Ambiguities resolved

- Marketable signal-bar levels closed one bar late. Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
