# #439378 Cryptocurrency Trend Following Strategy Based on Heiken Ashi -> `fmz_439378_smoothed_heikin_ashi_cross_long`

- FMZ source id: 439378 (lineage).
- Source: https://www.fmz.com/strategy/439378 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 17:40:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent stop from the fill |
| 2 | PASS | Smoothed Heikin-Ashi crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1_len` [50, 20] x `ma2_len` [100, 50]: **4 trials**; the 7.5 % stop fixed.

## Ambiguities resolved

- Tick stop of 7.5 % of the close read as 7.5 % of the fill. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
