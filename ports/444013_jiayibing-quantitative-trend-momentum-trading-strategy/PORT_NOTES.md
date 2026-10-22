# #444013 JiaYiBing Quantitative Trend Momentum Trading Strategy -> `fmz_444013_sma23_cross_outside_band_trail_take_profit`

- FMZ source id: 444013 (lineage).
- Source: https://www.fmz.com/strategy/444013 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 15:40:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the flat-time bracket as house stops, the per-bar stop pending |
| 2 | PASS | SMA crossings beyond the bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based quantity and cap stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma` [23, 50] x `stop_pct` [0.005, 0.01]: **4 trials**; the band, the activation and the trail step fixed.

## Ambiguities resolved

- Flat-time bracket as house stops; the per-bar close stop pending. Entries only from flat. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`trailing_stop, trailing_stop_pending, coarse_bar_stop`
