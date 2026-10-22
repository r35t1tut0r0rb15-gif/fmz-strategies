# #489006 Multi Timeframe Smart Money Concept Support and Resistance Dynamic Trading Strategy -> `fmz_489006_ema9_21_cross_swing_ltf_sma50_filters_pct_bracket_reversal`

- FMZ source id: 489006 (lineage).
- Source: https://www.fmz.com/strategy/489006 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 09:58:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | ADAPT | The pip bracket read as a percent at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bracket_pct` [3.333, 6.667] x `swing` [50, 20]: **4 trials**; EMA 9 / 21, 5- / 15-minute SMA 50, TR filter 1.5.

## Ambiguities resolved

- Lower-frame values are each block's last 5- / 15-minute bar; pips read at ETH 3000. Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "2D" (two broker days). MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
