# #363970 Johnys BOT -> `fmz_363970_adx_cloud_sar_range_filter_macd_volume_rsi_confluence_reversal`

- FMZ source id: 363970 (lineage).
- Source: https://www.fmz.com/strategy/363970 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-18 10:24:18). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; short-only bracket as fractions of the fill |
| 2 | PASS | Multi-indicator trend confluence with shortcuts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 10000 and commission 0.04 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`volume_f` [0.8, 1.2] x `th` [15.0, 25.0]: **4 trials**; the other settings as written.

## Ambiguities resolved

- The shared exit id leaves longs without a bracket, as written (weird case). Bracket re-sent with each close (pending).
- One tick read at 2.381e-06 of the level. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
